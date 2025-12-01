import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import JobQueue from './JobQueue'
import './ToolsPanel.css'

function ToolsPanel({ authenticated, apiBaseUrl }) {
  const { t } = useTranslation()
  const [extracting, setExtracting] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const handleExtractAliases = async () => {
    setExtracting(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await axios.post(`${apiBaseUrl}/api/batch/extract-aliases`)
      setMessage({
        type: 'success',
        text: response.data.message
      })
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || t('tools.aliasExtractor.error')
      })
    } finally {
      setExtracting(false)
    }
  }

  return (
    <div className="attribute-injector">
      <h2>{t('tools.aliasExtractor.title')}</h2>
      <p className="tool-description">{t('tools.aliasExtractor.description')}</p>

      {!authenticated && (
        <div className="alert alert-warning">
          {t('tools.aliasExtractor.authRequired')}
        </div>
      )}

      {message.text && (
        <div className={`alert alert-${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="btn-group" style={{ marginTop: '1.5rem' }}>
        <button
          onClick={handleExtractAliases}
          disabled={!authenticated || extracting}
          className="btn btn-primary"
        >
          {extracting ? (
            <>
              <div className="spinner"></div>
              {t('tools.aliasExtractor.extracting')}
            </>
          ) : (
            t('tools.aliasExtractor.button')
          )}
        </button>
      </div>

      <JobQueue apiBaseUrl={apiBaseUrl} jobType="alias_extraction" />
    </div>
  )
}

export default ToolsPanel
