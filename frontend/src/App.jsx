import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { LogOut } from 'lucide-react'
import AuthPanel from './components/AuthPanel'
import Sidebar from './components/Sidebar'
import ToolsPanel from './components/ToolsPanel'
import AttributeInjector from './components/AttributeInjector'
import OUGroupSync from './components/OUGroupSync'
import LanguageSelector from './components/LanguageSelector'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const { t } = useTranslation()
  const [currentTool, setCurrentTool] = useState('alias-extractor')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(
    localStorage.getItem('sidebarCollapsed') === 'true'
  )
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

  useEffect(() => {
    const handleStorageChange = () => {
      setSidebarCollapsed(localStorage.getItem('sidebarCollapsed') === 'true')
    }
    window.addEventListener('storage', handleStorageChange)
    // Also listen to custom event for same-window updates
    window.addEventListener('sidebarToggle', handleStorageChange)
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('sidebarToggle', handleStorageChange)
    }
  }, [])

  const renderTool = () => {
    if (!authStatus.authenticated) {
      return (
        <div className="max-w-2xl mx-auto">
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
      case 'group-sync':
        return <OUGroupSync apiBaseUrl={API_BASE_URL} />
      default:
        return <div>{t('common.error')}: Tool not found</div>
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar
        currentTool={currentTool}
        onToolChange={setCurrentTool}
        authStatus={authStatus}
      />

      <div className="flex flex-col min-h-screen transition-all duration-300" style={{ marginLeft: sidebarCollapsed ? '80px' : '288px' }}>
        <header className="bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">{t('app.title')}</h1>
                <p className="mt-1 text-primary-100 text-sm">{t('app.subtitle')}</p>
              </div>
              <div className="flex items-center gap-4">
                {authStatus.authenticated && (
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-3 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20">
                      <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                      <span className="text-sm font-medium">{authStatus.adminEmail}</span>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-lg border border-white/20 transition-all hover:scale-105 group"
                      title={t('auth.logout')}
                    >
                      <LogOut className="w-4 h-4 group-hover:rotate-12 transition-transform" />
                      <span className="text-sm font-medium">Logout</span>
                    </button>
                  </div>
                )}
                <LanguageSelector />
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="py-6">
            {renderTool()}
          </div>
        </main>

        <footer className="bg-white border-t border-gray-200 py-4">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <p className="text-center text-sm text-gray-600">
              GWorkspace Toolbox v1.0.0 - Tools for Google Workspace Administrators
            </p>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App
