import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import AuthPanel from './components/AuthPanel'
import Sidebar from './components/Sidebar'
import ToolsPanel from './components/ToolsPanel'
import AttributeInjector from './components/AttributeInjector'
import LanguageSelector from './components/LanguageSelector'
import axios from 'axios'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const { t } = useTranslation()
  const [currentTool, setCurrentTool] = useState('alias-extractor')
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

  const handleLogout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/auth/logout`)
      await checkAuthStatus()
    } catch (error) {
      console.error('Logout failed:', error)
      // Still refresh status even if logout fails
      await checkAuthStatus()
    }
  }

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const renderTool = () => {
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

    switch (currentTool) {
      case 'alias-extractor':
        return <ToolsPanel authenticated={authStatus.authenticated} apiBaseUrl={API_BASE_URL} />
      case 'attribute-injector':
        return <AttributeInjector apiBaseUrl={API_BASE_URL} />
      default:
        return <div>{t('common.error')}: Tool not found</div>
    }
  }

  return (
    <div className="app app-with-sidebar">
      <Sidebar
        currentTool={currentTool}
        onToolChange={setCurrentTool}
        authStatus={authStatus}
      />

      <div className="app-content">
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
                <button onClick={handleLogout} className="btn-logout" title={t('auth.logout')}>
                  🚪
                </button>
              </div>
            )}
            <LanguageSelector />
          </div>
        </header>

        <main className="app-main">
          <div className="container">
            {renderTool()}
          </div>
        </main>

        <footer className="app-footer">
          <p>DEA Toolbox v1.0.0 - Tools for AD Administrators</p>
        </footer>
      </div>
    </div>
  )
}

export default App
