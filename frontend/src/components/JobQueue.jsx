import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import JobCard from './JobCard'
import './JobQueue.css'

function JobQueue({ apiBaseUrl }) {
  const { t } = useTranslation()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchJobs()
    // Poll for updates every 2 seconds for more responsive UI
    const interval = setInterval(fetchJobs, 2000)
    return () => clearInterval(interval)
  }, [apiBaseUrl])

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/batch/jobs`)
      setJobs(response.data.jobs || [])
      setError('')
    } catch (err) {
      if (err.response?.status !== 401) {
        setError(err.response?.data?.detail || 'Failed to fetch jobs')
      }
    } finally {
      setLoading(false)
    }
  }

  const hasActiveJobs = jobs.some(job =>
    job.status === 'pending' || job.status === 'running'
  )

  if (loading && jobs.length === 0) {
    return (
      <div className="job-queue">
        <div className="job-queue-header">
          <h3>{t('tools.jobQueue.title')}</h3>
        </div>
        <div className="loading-message">
          {t('tools.jobQueue.loading')}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="job-queue">
        <div className="job-queue-header">
          <h3>{t('tools.jobQueue.title')}</h3>
        </div>
        <div className="error-message">
          {error}
        </div>
      </div>
    )
  }

  if (jobs.length === 0) {
    return (
      <div className="job-queue">
        <div className="job-queue-header">
          <h3>{t('tools.jobQueue.title')}</h3>
        </div>
        <div className="empty-state">
          <p>{t('tools.jobQueue.noJobs')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="job-queue">
      <div className="job-queue-header">
        <h3>{t('tools.jobQueue.title')}</h3>
        {hasActiveJobs && (
          <span className="active-indicator">
            <span className="pulse-dot"></span>
            {t('tools.jobQueue.activeJobs')}
          </span>
        )}
      </div>

      <div className="jobs-list">
        {jobs.map(job => (
          <JobCard
            key={job.job_uuid}
            job={job}
            apiBaseUrl={apiBaseUrl}
          />
        ))}
      </div>
    </div>
  )
}

export default JobQueue
