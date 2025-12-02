import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import {
  FolderTree,
  Plus,
  RefreshCw,
  Download,
  Upload,
  Trash2,
  Play,
  Clock,
  ChevronRight,
  Loader2,
  Mail,
  X
} from 'lucide-react'
import JobQueue from './JobQueue'

function OUGroupSync({ apiBaseUrl }) {
  const { t } = useTranslation()
  const [ous, setOus] = useState([])
  const [selectedOus, setSelectedOus] = useState([])
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [groupEmail, setGroupEmail] = useState('')
  const [groupName, setGroupName] = useState('')
  const [groupDescription, setGroupDescription] = useState('')
  const [configs, setConfigs] = useState([])
  const [loadingConfigs, setLoadingConfigs] = useState(false)
  const [importing, setImporting] = useState(false)
  const [syncingAll, setSyncingAll] = useState(false)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    fetchOUs()
    fetchConfigs()
  }, [])

  const fetchOUs = async () => {
    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await axios.get(`${apiBaseUrl}/api/tools/organizational-units`)
      setOus(response.data.organizational_units || [])
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || t('tools.attributeInjector.errorFetchingOUs')
      })
    } finally {
      setLoading(false)
    }
  }

  const fetchConfigs = async () => {
    setLoadingConfigs(true)
    try {
      const response = await axios.get(`${apiBaseUrl}/api/group-sync/configs`)
      setConfigs(response.data.configs || [])
    } catch (error) {
      console.error('Failed to fetch configs:', error)
    } finally {
      setLoadingConfigs(false)
    }
  }

  const toggleOU = (ouPath) => {
    setSelectedOus(prev => {
      if (prev.includes(ouPath)) {
        return prev.filter(p => p !== ouPath)
      } else {
        return [...prev, ouPath]
      }
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (selectedOus.length === 0) {
      setMessage({
        type: 'error',
        text: t('tools.groupSync.selectAtLeastOneOU')
      })
      return
    }

    if (!groupEmail) {
      setMessage({
        type: 'error',
        text: t('tools.groupSync.groupEmailRequired')
      })
      return
    }

    setSyncing(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await axios.post(`${apiBaseUrl}/api/batch/sync-ou-groups`, {
        ou_paths: selectedOus,
        group_email: groupEmail,
        group_name: groupName || groupEmail.split('@')[0],
        group_description: groupDescription
      })

      setMessage({
        type: 'success',
        text: `${t('tools.groupSync.jobCreated')} ${response.data.ou_count} ${t('tools.groupSync.ousQueued')}`
      })

      // Clear form
      setSelectedOus([])
      setGroupEmail('')
      setGroupName('')
      setGroupDescription('')
      setShowModal(false)

      // Refresh configs list
      fetchConfigs()
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.message || t('tools.groupSync.error')
      })
    } finally {
      setSyncing(false)
    }
  }

  const handleResync = async (configUuid) => {
    try {
      const response = await axios.post(`${apiBaseUrl}/api/group-sync/configs/${configUuid}/sync`)
      setMessage({
        type: 'success',
        text: t('tools.groupSync.resyncStarted')
      })
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || t('tools.groupSync.resyncError')
      })
    }
  }

  const handleDeleteConfig = async (configUuid) => {
    if (!confirm(t('tools.groupSync.confirmDelete'))) {
      return
    }

    try {
      await axios.delete(`${apiBaseUrl}/api/group-sync/configs/${configUuid}`)
      setMessage({
        type: 'success',
        text: t('tools.groupSync.configDeleted')
      })
      fetchConfigs()
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || t('tools.groupSync.deleteError')
      })
    }
  }

  const handleExportAll = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/group-sync/configs/export-all`, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url

      const contentDisposition = response.headers['content-disposition']
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `group_sync_configs_${new Date().toISOString().slice(0, 10)}.json`

      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()

      setMessage({
        type: 'success',
        text: t('tools.groupSync.exportSuccess')
      })
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || t('tools.groupSync.exportError')
      })
    }
  }

  const handleExportSingle = async (configUuid) => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/group-sync/configs/${configUuid}/export`, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url

      const contentDisposition = response.headers['content-disposition']
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `group_sync_config_${configUuid}.json`

      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()

      setMessage({
        type: 'success',
        text: t('tools.groupSync.exportSuccess')
      })
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || t('tools.groupSync.exportError')
      })
    }
  }

  const handleImport = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setImporting(true)
    setMessage({ type: '', text: '' })

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`${apiBaseUrl}/api/group-sync/configs/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setMessage({
        type: 'success',
        text: `${t('tools.groupSync.importSuccess')}: ${response.data.imported} ${t('tools.groupSync.imported')}, ${response.data.skipped} ${t('tools.groupSync.skipped')}`
      })

      fetchConfigs()
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || t('tools.groupSync.importError')
      })
    } finally {
      setImporting(false)
      event.target.value = ''
    }
  }

  const handleSyncAll = async () => {
    if (!confirm(t('tools.groupSync.confirmSyncAll'))) {
      return
    }

    setSyncingAll(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await axios.post(`${apiBaseUrl}/api/group-sync/configs/sync-all`)

      setMessage({
        type: 'success',
        text: `${t('tools.groupSync.syncAllStarted')}: ${response.data.jobs_created} ${t('tools.groupSync.jobsCreated')}`
      })

      fetchConfigs()
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || t('tools.groupSync.syncAllError')
      })
    } finally {
      setSyncingAll(false)
    }
  }

  const buildOUTree = () => {
    const tree = []
    const ouMap = {}

    ous.forEach(ou => {
      ouMap[ou.path] = {
        ...ou,
        children: []
      }
    })

    ous.forEach(ou => {
      if (ou.parent_path && ouMap[ou.parent_path]) {
        ouMap[ou.parent_path].children.push(ouMap[ou.path])
      } else {
        tree.push(ouMap[ou.path])
      }
    })

    return tree
  }

  const renderOUNode = (node, level = 0) => {
    const isSelected = selectedOus.includes(node.path)
    const hasChildren = node.children && node.children.length > 0

    return (
      <div key={node.path} style={{ marginLeft: `${level * 20}px` }} className="mb-1">
        <label className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => toggleOU(node.path)}
            className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-2 focus:ring-primary-500"
          />
          <div className="flex items-center gap-2 flex-1">
            {hasChildren && <ChevronRight className="w-4 h-4 text-gray-400" />}
            <FolderTree className="w-4 h-4 text-gray-500" />
            <span className="font-medium text-gray-700">{node.name}</span>
            <span className="text-xs text-gray-400 ml-auto">{node.path}</span>
          </div>
        </label>
        {hasChildren && (
          <div className="ml-4">
            {node.children.map(child => renderOUNode(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  const ouTree = buildOUTree()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">{t('tools.groupSync.title')}</h2>
          <p className="mt-1 text-sm text-gray-600">{t('tools.groupSync.description')}</p>
        </div>
        <button
          onClick={() => {
            setShowModal(true)
            fetchOUs()
          }}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium shadow-sm"
        >
          <Plus className="w-5 h-5" />
          {t('tools.groupSync.newConfig')}
        </button>
      </div>

      {message.text && (
        <div className={`p-4 rounded-lg border ${
          message.type === 'success'
            ? 'bg-green-50 border-green-200 text-green-800'
            : 'bg-red-50 border-red-200 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

      {/* Saved Configurations Section */}
      {configs.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900">{t('tools.groupSync.savedConfigs')}</h3>
            <div className="flex items-center gap-3">
              <button
                onClick={handleSyncAll}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium shadow-sm disabled:opacity-50"
                disabled={syncingAll || configs.length === 0}
              >
                {syncingAll ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    {t('common.loading')}
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    {t('tools.groupSync.syncAllButton')}
                  </>
                )}
              </button>
              <label className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg cursor-pointer transition-colors font-medium shadow-sm">
                {importing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    {t('common.loading')}
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    {t('tools.groupSync.importButton')}
                  </>
                )}
                <input
                  type="file"
                  accept=".json"
                  onChange={handleImport}
                  className="hidden"
                  disabled={importing}
                />
              </label>
              <button
                onClick={handleExportAll}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg transition-colors font-medium shadow-sm"
              >
                <Download className="w-4 h-4" />
                {t('tools.groupSync.exportAllButton')}
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {configs.map(config => (
              <div key={config.config_uuid} className="border border-gray-200 rounded-lg p-5 hover:border-primary-300 hover:shadow-sm transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <Mail className="w-5 h-5 text-primary-600 flex-shrink-0" />
                    <div>
                      <span className="font-semibold text-gray-900 block">{config.group_email}</span>
                      <span className="text-sm text-gray-500">
                        {config.ou_paths.length} {t('tools.groupSync.ousInConfig')}
                      </span>
                    </div>
                  </div>
                  {config.last_synced_at && (
                    <div className="flex items-center gap-1.5 text-xs text-gray-500">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{t('tools.groupSync.lastSynced')}: {new Date(config.last_synced_at).toLocaleString()}</span>
                    </div>
                  )}
                </div>

                {config.group_description && (
                  <p className="text-sm text-gray-600 mb-3 ml-8">
                    {config.group_description}
                  </p>
                )}

                <div className="flex items-center justify-end">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleResync(config.config_uuid)}
                      className="inline-flex items-center gap-1.5 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium shadow-sm"
                    >
                      <RefreshCw className="w-4 h-4" />
                      {t('tools.groupSync.resyncButton')}
                    </button>
                    <button
                      onClick={() => handleExportSingle(config.config_uuid)}
                      className="inline-flex items-center gap-1.5 px-3 py-2 text-sm bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg transition-colors font-medium shadow-sm"
                    >
                      <Download className="w-4 h-4" />
                      {t('tools.groupSync.exportButton')}
                    </button>
                    <button
                      onClick={() => handleDeleteConfig(config.config_uuid)}
                      className="inline-flex items-center gap-1.5 px-3 py-2 text-sm bg-red-50 border border-red-200 hover:bg-red-100 text-red-700 rounded-lg transition-colors font-medium shadow-sm"
                    >
                      <Trash2 className="w-4 h-4" />
                      {t('common.delete')}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal for Create New Sync Configuration */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <Plus className="w-5 h-5 text-primary-600" />
                {t('tools.groupSync.newConfig')}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6">
              {loading ? (
                <div className="flex items-center justify-center gap-3 py-8">
                  <Loader2 className="w-5 h-5 animate-spin text-primary-600" />
                  <span className="text-gray-600">{t('common.loading')}</span>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                <FolderTree className="w-4 h-4" />
                {t('tools.groupSync.selectOUs')}
              </h4>
              <div className="border border-gray-200 rounded-lg p-4 max-h-64 overflow-y-auto bg-gray-50">
                {ouTree.length === 0 ? (
                  <p className="text-gray-500 text-sm text-center py-4">
                    {t('tools.attributeInjector.noOUs')}
                  </p>
                ) : (
                  ouTree.map(node => renderOUNode(node))
                )}
              </div>
              {selectedOus.length > 0 && (
                <div className="mt-2 text-sm text-gray-600">
                  {t('tools.attributeInjector.selectedOUs')}: <span className="font-medium">{selectedOus.length}</span>
                </div>
              )}
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">{t('tools.groupSync.groupSettings')}</h4>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('tools.groupSync.groupEmail')} *
                  </label>
                  <input
                    type="email"
                    value={groupEmail}
                    onChange={(e) => setGroupEmail(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder={t('tools.groupSync.groupEmailPlaceholder')}
                    required
                  />
                  <p className="mt-1 text-xs text-gray-500">{t('tools.groupSync.groupEmailHelp')}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('tools.groupSync.groupName')}
                  </label>
                  <input
                    type="text"
                    value={groupName}
                    onChange={(e) => setGroupName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder={t('tools.groupSync.groupNamePlaceholder')}
                  />
                  <p className="mt-1 text-xs text-gray-500">{t('tools.groupSync.groupNameHelp')}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('tools.groupSync.groupDescription')}
                  </label>
                  <textarea
                    value={groupDescription}
                    onChange={(e) => setGroupDescription(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder={t('tools.groupSync.groupDescriptionPlaceholder')}
                    rows="3"
                  />
                  <p className="mt-1 text-xs text-gray-500">{t('tools.groupSync.groupDescriptionHelp')}</p>
                </div>
              </div>
            </div>

                  <div className="flex items-center justify-end gap-3">
                    <button
                      type="button"
                      onClick={() => setShowModal(false)}
                      className="px-4 py-2 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                    >
                      {t('common.cancel')}
                    </button>
                    <button
                      type="submit"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={syncing || selectedOus.length === 0 || !groupEmail}
                    >
                      {syncing ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          {t('tools.groupSync.syncing')}
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4" />
                          {t('tools.groupSync.syncButton')}
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}

      <JobQueue apiBaseUrl={apiBaseUrl} jobType="group_sync" />
    </div>
  )
}

export default OUGroupSync
