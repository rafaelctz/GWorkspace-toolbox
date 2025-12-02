import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import {
  Clock,
  Loader2,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronRight,
  RotateCcw,
  Download,
  Eye,
  EyeOff,
  Calendar,
  Users,
  AlertTriangle,
  TrendingUp
} from 'lucide-react'

function JobCard({ job, apiBaseUrl }) {
  const { t } = useTranslation()
  const [expanded, setExpanded] = useState(false)
  const [failedUsers, setFailedUsers] = useState([])
  const [loadingFailed, setLoadingFailed] = useState(false)
  const [showFailedUsers, setShowFailedUsers] = useState(false)
  const [restarting, setRestarting] = useState(false)

  const getStatusColors = (status) => {
    switch (status) {
      case 'pending':
        return { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-200' }
      case 'running':
        return { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' }
      case 'completed':
        return { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200' }
      case 'failed':
        return { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-200' }
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-200' }
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4" />
      case 'running':
        return <Loader2 className="w-4 h-4 animate-spin" />
      case 'completed':
        return <CheckCircle2 className="w-4 h-4" />
      case 'failed':
        return <XCircle className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
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

  const fetchFailedUsers = async () => {
    if (failedUsers.length > 0) {
      setShowFailedUsers(!showFailedUsers)
      return
    }

    setLoadingFailed(true)
    try {
      const response = await axios.get(
        `${apiBaseUrl}/api/batch/jobs/${job.job_uuid}/failed-users`
      )
      setFailedUsers(response.data.failed_users || [])
      setShowFailedUsers(true)
    } catch (error) {
      console.error('Failed to load failed users:', error)
    } finally {
      setLoadingFailed(false)
    }
  }

  const restartJob = async (e) => {
    e.stopPropagation()
    if (restarting) return

    setRestarting(true)
    try {
      await axios.post(`${apiBaseUrl}/api/batch/jobs/${job.job_uuid}/restart`)
    } catch (error) {
      console.error('Failed to restart job:', error)
      alert(error.response?.data?.detail || 'Failed to restart job')
    } finally {
      setRestarting(false)
    }
  }

  const statusColors = getStatusColors(job.status)

  return (
    <div className={`border ${statusColors.border} rounded-lg overflow-hidden transition-all hover:shadow-sm`}>
      <div
        className={`${statusColors.bg} px-5 py-4 cursor-pointer`}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start gap-4">
          <div className={`flex items-center gap-2 ${statusColors.text} font-medium text-sm`}>
            {getStatusIcon(job.status)}
            <span>{t(`tools.jobQueue.status.${job.status}`)}</span>
          </div>

          <div className="flex-1 min-w-0">
            <div className="text-sm text-gray-900 truncate">
              <span className="font-semibold">{job.attribute}</span>
              <span className="mx-2 text-gray-400">→</span>
              <span className="font-medium">{job.value}</span>
            </div>
            <div className="text-sm text-gray-600 truncate mt-1">
              {formatOUPaths(job.ou_paths)}
            </div>
          </div>

          <div className="flex items-center gap-4 flex-shrink-0">
            <div className="flex items-center gap-2 text-sm">
              <Users className="w-4 h-4 text-gray-500" />
              <span className="font-medium text-gray-700">{job.total_users}</span>
            </div>
            {job.status === 'running' && (
              <div className="flex items-center gap-2 text-sm">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                <span className="font-medium text-blue-700">{Math.round(job.progress_percentage)}%</span>
              </div>
            )}
            {job.status === 'completed' && (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  <span className="font-medium text-green-700">{job.successful_users}</span>
                </div>
                {job.failed_users > 0 && (
                  <div className="flex items-center gap-1 text-sm">
                    <XCircle className="w-4 h-4 text-red-600" />
                    <span className="font-medium text-red-700">{job.failed_users}</span>
                  </div>
                )}
              </div>
            )}
            <button
              className="text-gray-600 hover:text-gray-900 transition-colors"
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                setExpanded(!expanded)
              }}
            >
              {expanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {(job.status === 'running' || job.status === 'completed') && (
        <div className="relative h-2 bg-gray-200">
          <div
            className={`absolute top-0 left-0 h-full transition-all ${
              job.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'
            }`}
            style={{ width: `${job.progress_percentage}%` }}
          />
        </div>
      )}

      {expanded && (
        <div className="bg-white px-5 py-4 border-t border-gray-200">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-500">{t('tools.jobQueue.jobId')}:</span>
                <span className="ml-2 font-mono text-gray-700 text-xs">{job.job_uuid}</span>
              </div>

              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span className="text-gray-500">{t('tools.jobQueue.created')}:</span>
                <span className="text-gray-700">{formatDate(job.created_at)}</span>
              </div>

              {job.started_at && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-500">{t('tools.jobQueue.started')}:</span>
                  <span className="text-gray-700">{formatDate(job.started_at)}</span>
                </div>
              )}

              {job.completed_at && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-500">{t('tools.jobQueue.completed')}:</span>
                  <span className="text-gray-700">{formatDate(job.completed_at)}</span>
                </div>
              )}
            </div>

            {job.error_message && (
              <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <span className="text-sm font-medium text-red-800">{t('tools.jobQueue.error')}:</span>
                  <span className="text-sm text-red-700 ml-2">{job.error_message}</span>
                </div>
              </div>
            )}

            {job.user_status_counts && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  {t('tools.jobQueue.userBreakdown')}
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="text-sm">
                    <span className="text-gray-500">{t('tools.jobQueue.userStatus.pending')}:</span>
                    <span className="ml-2 font-medium text-gray-700">{job.user_status_counts.pending || 0}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">{t('tools.jobQueue.userStatus.processing')}:</span>
                    <span className="ml-2 font-medium text-gray-700">{job.user_status_counts.processing || 0}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-green-600">{t('tools.jobQueue.userStatus.success')}:</span>
                    <span className="ml-2 font-medium text-green-700">{job.user_status_counts.success || 0}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-red-600">{t('tools.jobQueue.userStatus.failed')}:</span>
                    <span className="ml-2 font-medium text-red-700">{job.user_status_counts.failed || 0}</span>
                  </div>
                </div>
              </div>
            )}

            <div className="flex flex-wrap gap-2 pt-3 border-t border-gray-100">
              {(job.status === 'pending' || job.status === 'failed') && (
                <button
                  onClick={restartJob}
                  className="inline-flex items-center gap-2 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium disabled:opacity-50"
                  disabled={restarting}
                >
                  {restarting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Restarting...
                    </>
                  ) : (
                    <>
                      <RotateCcw className="w-4 h-4" />
                      Restart Job
                    </>
                  )}
                </button>
              )}

              {job.status === 'completed' && job.job_type === 'alias_extraction' && job.file_path && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    const downloadUrl = `${apiBaseUrl}/api/tools/download-aliases?file_path=${encodeURIComponent(job.file_path)}`
                    window.open(downloadUrl, '_blank')
                  }}
                  className="inline-flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                >
                  <Download className="w-4 h-4" />
                  Download CSV
                </button>
              )}

              {job.failed_users > 0 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    fetchFailedUsers()
                  }}
                  className="inline-flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium disabled:opacity-50"
                  disabled={loadingFailed}
                >
                  {loadingFailed ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      {t('common.loading')}
                    </>
                  ) : showFailedUsers ? (
                    <>
                      <EyeOff className="w-4 h-4" />
                      Hide Failed Users ({job.failed_users})
                    </>
                  ) : (
                    <>
                      <Eye className="w-4 h-4" />
                      View Failed Users ({job.failed_users})
                    </>
                  )}
                </button>
              )}
            </div>

            {showFailedUsers && failedUsers.length > 0 && (
              <div className="mt-3 border border-gray-200 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-gray-50 border-b border-gray-200">
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">OU Path</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Error</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {failedUsers.map((user, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-4 py-2 font-mono text-xs text-gray-700">{user.email}</td>
                          <td className="px-4 py-2 text-xs text-gray-600">{user.ou_path}</td>
                          <td className="px-4 py-2 text-xs text-red-600">{user.error_message}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default JobCard
