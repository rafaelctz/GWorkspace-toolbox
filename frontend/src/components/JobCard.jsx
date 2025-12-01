import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import './JobCard.css'

function JobCard({ job, apiBaseUrl }) {
  const { t } = useTranslation()
  const [expanded, setExpanded] = useState(false)

  const getStatusClass = (status) => {
    switch (status) {
      case 'pending': return 'status-pending'
      case 'running': return 'status-running'
      case 'completed': return 'status-completed'
      case 'failed': return 'status-failed'
      default: return ''
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return '⏳'
      case 'running': return '⚙️'
      case 'completed': return '✅'
      case 'failed': return '❌'
      default: return '•'
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return '—'
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  const formatOUPaths = (ouPaths) => {
    try {
      const paths = typeof ouPaths === 'string' ? JSON.parse(ouPaths) : ouPaths
      if (paths.length === 1) return paths[0]
      return `${paths.length} ${t('tools.jobQueue.organizationalUnits')}`
    } catch {
      return ouPaths
    }
  }

  return (
    <div className={`job-card ${getStatusClass(job.status)}`}>
      <div className="job-card-header" onClick={() => setExpanded(!expanded)}>
        <div className="job-status">
          <span className="status-icon">{getStatusIcon(job.status)}</span>
          <span className="status-text">
            {t(`tools.jobQueue.status.${job.status}`)}
          </span>
        </div>

        <div className="job-info">
          <div className="job-attribute">
            <strong>{job.attribute}</strong> = {job.value}
          </div>
          <div className="job-ou">
            {formatOUPaths(job.ou_paths)}
          </div>
        </div>

        <div className="job-stats">
          <div className="stat">
            <span className="stat-label">{t('tools.jobQueue.totalUsers')}</span>
            <span className="stat-value">{job.total_users}</span>
          </div>
          {job.status === 'running' && (
            <div className="stat">
              <span className="stat-label">{t('tools.jobQueue.progress')}</span>
              <span className="stat-value">{Math.round(job.progress_percentage)}%</span>
            </div>
          )}
          {job.status === 'completed' && (
            <>
              <div className="stat success">
                <span className="stat-label">{t('tools.jobQueue.successful')}</span>
                <span className="stat-value">{job.successful_users}</span>
              </div>
              {job.failed_users > 0 && (
                <div className="stat failed">
                  <span className="stat-label">{t('tools.jobQueue.failed')}</span>
                  <span className="stat-value">{job.failed_users}</span>
                </div>
              )}
            </>
          )}
        </div>

        <button className="expand-button" type="button">
          {expanded ? '▼' : '▶'}
        </button>
      </div>

      {(job.status === 'running' || job.status === 'completed') && (
        <div className="progress-bar-container">
          <div
            className="progress-bar-fill"
            style={{ width: `${job.progress_percentage}%` }}
          />
          <span className="progress-text">
            {job.processed_users} / {job.total_users} {t('tools.jobQueue.usersProcessed')}
          </span>
        </div>
      )}

      {expanded && (
        <div className="job-card-details">
          <div className="detail-row">
            <span className="detail-label">{t('tools.jobQueue.jobId')}:</span>
            <span className="detail-value mono">{job.job_uuid}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">{t('tools.jobQueue.created')}:</span>
            <span className="detail-value">{formatDate(job.created_at)}</span>
          </div>

          {job.started_at && (
            <div className="detail-row">
              <span className="detail-label">{t('tools.jobQueue.started')}:</span>
              <span className="detail-value">{formatDate(job.started_at)}</span>
            </div>
          )}

          {job.completed_at && (
            <div className="detail-row">
              <span className="detail-label">{t('tools.jobQueue.completed')}:</span>
              <span className="detail-value">{formatDate(job.completed_at)}</span>
            </div>
          )}

          {job.error_message && (
            <div className="detail-row error">
              <span className="detail-label">{t('tools.jobQueue.error')}:</span>
              <span className="detail-value">{job.error_message}</span>
            </div>
          )}

          {job.user_status_counts && (
            <div className="user-counts">
              <h4>{t('tools.jobQueue.userBreakdown')}:</h4>
              <div className="counts-grid">
                <div className="count-item">
                  <span className="count-label">{t('tools.jobQueue.userStatus.pending')}:</span>
                  <span className="count-value">{job.user_status_counts.pending || 0}</span>
                </div>
                <div className="count-item">
                  <span className="count-label">{t('tools.jobQueue.userStatus.processing')}:</span>
                  <span className="count-value">{job.user_status_counts.processing || 0}</span>
                </div>
                <div className="count-item success">
                  <span className="count-label">{t('tools.jobQueue.userStatus.success')}:</span>
                  <span className="count-value">{job.user_status_counts.success || 0}</span>
                </div>
                <div className="count-item failed">
                  <span className="count-label">{t('tools.jobQueue.userStatus.failed')}:</span>
                  <span className="count-value">{job.user_status_counts.failed || 0}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default JobCard
