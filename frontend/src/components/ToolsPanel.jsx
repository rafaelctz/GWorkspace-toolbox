import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import './ToolsPanel.css'

function ToolsPanel({ authenticated, apiBaseUrl }) {
  const { t } = useTranslation()
  const [extracting, setExtracting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleExtractAliases = async () => {
    setExtracting(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post(`${apiBaseUrl}/api/tools/extract-aliases`)
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || t('tools.aliasExtractor.error'))
    } finally {
      setExtracting(false)
    }
  }

  const handleDownload = () => {
    if (result?.file_path) {
      const downloadUrl = `${apiBaseUrl}/api/tools/download-aliases?file_path=${encodeURIComponent(result.file_path)}`
      window.open(downloadUrl, '_blank')
    }
  }

  return (
    <div className="card">
      <h2>{t('tools.title')}</h2>

      <div className="tool-card">
        <h3>{t('tools.aliasExtractor.title')}</h3>
        <p className="tool-description">{t('tools.aliasExtractor.description')}</p>

        {!authenticated && (
          <div className="alert alert-warning">
            ⚠️ {t('tools.aliasExtractor.authRequired')}
          </div>
        )}

        {error && (
          <div className="alert alert-error">
            ❌ {error}
          </div>
        )}

        {result && (
          <div className="result-panel">
            <div className="alert alert-success">
              ✅ {t('tools.aliasExtractor.success')}
            </div>

            <div className="result-stats">
              <div className="stat-item">
                <span className="stat-label">{t('tools.aliasExtractor.totalUsers')}</span>
                <span className="stat-value">{result.total_users}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">{t('tools.aliasExtractor.usersWithAliases')}</span>
                <span className="stat-value">{result.users_with_aliases}</span>
              </div>
            </div>

            <button onClick={handleDownload} className="btn btn-success">
              📥 {t('tools.aliasExtractor.download')}
            </button>
          </div>
        )}

        <div className="btn-group" style={{ marginTop: '1rem' }}>
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
      </div>
    </div>
  )
}

export default ToolsPanel
