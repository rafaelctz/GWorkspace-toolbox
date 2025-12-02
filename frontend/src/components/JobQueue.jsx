import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { ListTodo, Activity, Loader2 } from 'lucide-react'
import JobCard from './JobCard'

function JobQueue({ apiBaseUrl, jobType }) {
  const { t } = useTranslation()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchJobs()
    // Poll for updates every 2 seconds for more responsive UI
    const interval = setInterval(fetchJobs, 2000)
    return () => clearInterval(interval)
  }, [apiBaseUrl, jobType])

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/batch/jobs`)
      const allJobs = response.data.jobs || []
      // Filter by job type if provided
      const filteredJobs = jobType
        ? allJobs.filter(job => job.job_type === jobType)
        : allJobs
      setJobs(filteredJobs)
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
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <ListTodo className="w-5 h-5 text-gray-700" />
          <h3 className="text-lg font-semibold text-gray-800">{t('tools.jobQueue.title')}</h3>
        </div>
        <div className="flex items-center justify-center gap-3 py-8">
          <Loader2 className="w-5 h-5 animate-spin text-primary-600" />
          <span className="text-gray-600">{t('tools.jobQueue.loading')}</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <ListTodo className="w-5 h-5 text-gray-700" />
          <h3 className="text-lg font-semibold text-gray-800">{t('tools.jobQueue.title')}</h3>
        </div>
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      </div>
    )
  }

  if (jobs.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <ListTodo className="w-5 h-5 text-gray-700" />
          <h3 className="text-lg font-semibold text-gray-800">{t('tools.jobQueue.title')}</h3>
        </div>
        <div className="text-center py-8 text-gray-500">
          <p>{t('tools.jobQueue.noJobs')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <ListTodo className="w-5 h-5 text-gray-700" />
          <h3 className="text-xl font-semibold text-gray-900">{t('tools.jobQueue.title')}</h3>
        </div>
        {hasActiveJobs && (
          <div className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 border border-green-200 rounded-lg shadow-sm">
            <Activity className="w-4 h-4 animate-pulse" />
            <span className="text-sm font-medium">{t('tools.jobQueue.activeJobs')}</span>
          </div>
        )}
      </div>

      <div className="space-y-4">
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
