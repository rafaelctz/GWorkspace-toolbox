import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import JobQueue from './JobQueue'

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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('tools.aliasExtractor.title')}</h2>
        <p className="text-gray-600 mb-6">{t('tools.aliasExtractor.description')}</p>

        {!authenticated && (
          <div className="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-sm text-amber-800">{t('tools.aliasExtractor.authRequired')}</p>
          </div>
        )}

        {message.text && (
          <div className={`mb-4 p-4 rounded-lg border ${
            message.type === 'success'
              ? 'bg-green-50 border-green-200 text-green-800'
              : 'bg-red-50 border-red-200 text-red-800'
          }`}>
            {message.text}
          </div>
        )}

        <button
          onClick={handleExtractAliases}
          disabled={!authenticated || extracting}
          className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          {extracting ? (
            <>
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
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
