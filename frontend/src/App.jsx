import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import AuthPanel from './components/AuthPanel'
import ToolsPanel from './components/ToolsPanel'
import LanguageSelector from './components/LanguageSelector'
import axios from 'axios'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const { t } = useTranslation()
  const [authStatus, setAuthStatus] = useState({
    authenticated: false,
    adminEmail: null,
    domain: null,
    loading: true
  })

  const checkAuthStatus = async () => {
    // Set loading true only if we're not already in a loading state
    setAuthStatus(prev => ({ ...prev, loading: true }))

    try {
      const response = await axios.get(`${API_BASE_URL}/api/status`, {
        timeout: 10000 // 10 second timeout
      })
      setAuthStatus({
        ...response.data,
        loading: false
      })
    } catch (error) {
      console.error('Failed to check auth status:', error)
      setAuthStatus({
        authenticated: false,
        adminEmail: null,
        domain: null,
        loading: false
      })
    }
  }

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const renderContent = () => {
    if (!authStatus.authenticated) {
      return (
        <div className="auth-required-message">
          <h2>{t('auth.title')}</h2>
          <AuthPanel
            authStatus={authStatus}
            onAuthChange={checkAuthStatus}
            apiBaseUrl={API_BASE_URL}
          />
        </div>
      )
    }

    return <ToolsPanel authenticated={authStatus.authenticated} apiBaseUrl={API_BASE_URL} />
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>{t('app.title')}</h1>
          <p className="subtitle">{t('app.subtitle')}</p>
        </div>
        <div className="header-actions">
          {authStatus.authenticated && (
            <div className="auth-status">
              <span className="status-indicator active"></span>
              <span className="auth-email">{authStatus.adminEmail}</span>
            </div>
          )}
          <LanguageSelector />
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {renderContent()}
        </div>
      </main>

      <footer className="app-footer">
        <p>DEA Toolbox Light v1.0.0 - Alias Extractor for Google Workspace</p>
      </footer>
    </div>
  )
}

export default App
