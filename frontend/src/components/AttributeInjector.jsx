import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import JobQueue from './JobQueue'
import './AttributeInjector.css'

function AttributeInjector({ apiBaseUrl }) {
  const { t } = useTranslation()
  const [ous, setOus] = useState([])
  const [selectedOus, setSelectedOus] = useState([])
  const [loading, setLoading] = useState(false)
  const [injecting, setInjecting] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [attribute, setAttribute] = useState('')
  const [value, setValue] = useState('')
  const [useBatchMode, setUseBatchMode] = useState(true)

  // Common user attributes
  const attributes = [
    { value: 'title', label: t('tools.attributeInjector.attributes.title') },
    { value: 'department', label: t('tools.attributeInjector.attributes.department') },
    { value: 'employeeType', label: t('tools.attributeInjector.attributes.employeeType') },
    { value: 'costCenter', label: t('tools.attributeInjector.attributes.costCenter') },
    { value: 'buildingId', label: t('tools.attributeInjector.attributes.buildingId') },
    { value: 'manager', label: t('tools.attributeInjector.attributes.manager') }
  ]

  useEffect(() => {
    fetchOUs()
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
        text: t('tools.attributeInjector.selectAtLeastOneOU')
      })
      return
    }

    if (!attribute) {
      setMessage({
        type: 'error',
        text: t('tools.attributeInjector.selectAttribute')
      })
      return
    }

    if (!value) {
      setMessage({
        type: 'error',
        text: t('tools.attributeInjector.enterValue')
      })
      return
    }

    setInjecting(true)
    setMessage({ type: '', text: '' })

    console.log('=== Starting attribute injection ===')
    console.log('API Base URL:', apiBaseUrl)
    console.log('Selected OUs:', selectedOus)
    console.log('Attribute:', attribute)
    console.log('Value:', value)
    console.log('Batch Mode:', useBatchMode)

    try {
      const endpoint = useBatchMode
        ? `${apiBaseUrl}/api/batch/inject-attribute`
        : `${apiBaseUrl}/api/tools/inject-attribute`

      console.log('About to make POST request to:', endpoint)
      const response = await axios.post(endpoint, {
        ou_paths: selectedOus,
        attribute,
        value
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: useBatchMode ? 60000 : 300000, // 1 min for batch, 5 min for sync
        validateStatus: function (status) {
          return status >= 200 && status < 500;
        }
      })

      console.log('POST request completed successfully')
      console.log('Response:', response)
      console.log('Response data:', response.data)

      if (useBatchMode) {
        setMessage({
          type: 'success',
          text: `${t('tools.attributeInjector.batchJobCreated')} ${response.data.total_users} ${t('tools.attributeInjector.usersQueued')}`
        })
      } else {
        setMessage({
          type: 'success',
          text: `${t('tools.attributeInjector.success')} ${response.data.updated_count} ${t('tools.attributeInjector.usersUpdated')}`
        })
      }

      // Clear form
      setSelectedOus([])
      setAttribute('')
      setValue('')
    } catch (error) {
      console.error('Attribute injection error:', error)
      console.error('Error response:', error.response)
      console.error('Error request:', error.request)
      console.error('Error message:', error.message)

      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.message || t('tools.attributeInjector.error')
      })
    } finally {
      setInjecting(false)
    }
  }

  // Build OU tree structure
  const buildOUTree = () => {
    const tree = []
    const ouMap = {}

    // First pass: create all nodes
    ous.forEach(ou => {
      ouMap[ou.path] = {
        ...ou,
        children: []
      }
    })

    // Second pass: build tree structure
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
      <div key={node.path} className="ou-node" style={{ marginLeft: `${level * 20}px` }}>
        <label className="ou-checkbox">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => toggleOU(node.path)}
          />
          <span className="ou-name">
            {hasChildren && <span className="ou-icon">📁</span>}
            {!hasChildren && <span className="ou-icon">📄</span>}
            {node.name}
          </span>
          <span className="ou-path">{node.path}</span>
        </label>
        {hasChildren && (
          <div className="ou-children">
            {node.children.map(child => renderOUNode(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  const ouTree = buildOUTree()

  return (
    <div className="attribute-injector">
      <h2>{t('tools.attributeInjector.title')}</h2>
      <p className="tool-description">{t('tools.attributeInjector.description')}</p>

      {message.text && (
        <div className={`alert alert-${message.type}`}>
          {message.text}
        </div>
      )}

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <span>{t('common.loading')}</span>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="injector-form">
          <div className="form-section">
            <h3>{t('tools.attributeInjector.selectOUs')}</h3>
            <div className="ou-tree">
              {ouTree.length === 0 ? (
                <p className="no-ous">{t('tools.attributeInjector.noOUs')}</p>
              ) : (
                ouTree.map(node => renderOUNode(node))
              )}
            </div>
            {selectedOus.length > 0 && (
              <div className="selected-count">
                {t('tools.attributeInjector.selectedOUs')}: {selectedOus.length}
              </div>
            )}
          </div>

          <div className="form-section">
            <h3>{t('tools.attributeInjector.selectAttribute')}</h3>
            <select
              value={attribute}
              onChange={(e) => setAttribute(e.target.value)}
              className="form-select"
              required
            >
              <option value="">{t('tools.attributeInjector.chooseAttribute')}</option>
              {attributes.map(attr => (
                <option key={attr.value} value={attr.value}>
                  {attr.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-section">
            <h3>{t('tools.attributeInjector.enterValue')}</h3>
            <input
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="form-input"
              placeholder={t('tools.attributeInjector.valuePlaceholder')}
              required
            />
          </div>

          <div className="form-section batch-mode-toggle">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={useBatchMode}
                onChange={(e) => setUseBatchMode(e.target.checked)}
                className="toggle-checkbox"
              />
              <span className="toggle-text">
                {t('tools.attributeInjector.useBatchMode')}
              </span>
            </label>
            <p className="toggle-description">
              {useBatchMode
                ? t('tools.attributeInjector.batchModeDescription')
                : t('tools.attributeInjector.syncModeDescription')
              }
            </p>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={injecting || selectedOus.length === 0 || !attribute || !value}
          >
            {injecting
              ? t('tools.attributeInjector.injecting')
              : useBatchMode
                ? t('tools.attributeInjector.createBatchJob')
                : t('tools.attributeInjector.injectButton')
            }
          </button>
        </form>
      )}

      {useBatchMode && <JobQueue apiBaseUrl={apiBaseUrl} />}
    </div>
  )
}

export default AttributeInjector
