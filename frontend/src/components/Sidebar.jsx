import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Mail, Settings, Users, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react'

function Sidebar({ currentTool, onToolChange, authStatus }) {
  const { t } = useTranslation()
  const [collapsed, setCollapsed] = useState(
    localStorage.getItem('sidebarCollapsed') === 'true'
  )

  // Persist collapse state to localStorage
  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', collapsed)
  }, [collapsed])

  const tools = [
    {
      id: 'alias-extractor',
      name: t('tools.aliasExtractor.title'),
      icon: Mail,
      description: t('tools.aliasExtractor.description')
    },
    {
      id: 'attribute-injector',
      name: t('tools.attributeInjector.title'),
      icon: Settings,
      description: t('tools.attributeInjector.description')
    },
    {
      id: 'group-sync',
      name: t('tools.groupSync.title'),
      icon: Users,
      description: t('tools.groupSync.description')
    }
  ]

  const toggleSidebar = () => {
    setCollapsed(!collapsed)
    // Dispatch custom event to notify App component
    window.dispatchEvent(new Event('sidebarToggle'))
  }

  return (
    <div className={`fixed left-0 top-0 flex flex-col h-screen bg-white border-r border-gray-200 shadow-sm transition-all duration-300 z-40 ${collapsed ? 'w-20' : 'w-72'}`}>
      <div className="flex items-center justify-between px-6 py-5 border-b border-gray-200 bg-gray-50">
        {!collapsed && <h2 className="text-xl font-bold text-gray-900">{t('tools.title')}</h2>}
        <button
          className={`p-2.5 rounded-lg hover:bg-gray-200 transition-colors ${collapsed ? 'mx-auto' : ''}`}
          onClick={toggleSidebar}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5 text-gray-700" />
          ) : (
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          )}
        </button>
      </div>

      {!authStatus.authenticated && !collapsed && (
        <div className="mx-4 mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-amber-800">{t('tools.authRequired')}</p>
        </div>
      )}

      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        {tools.map(tool => {
          const IconComponent = tool.icon
          const isActive = currentTool === tool.id
          return (
            <button
              key={tool.id}
              className={`w-full flex items-center gap-3 px-4 py-3.5 mb-2 rounded-xl transition-all font-medium ${
                isActive
                  ? 'bg-primary-600 text-white shadow-md shadow-primary-200'
                  : 'text-gray-700 hover:bg-gray-100'
              } ${
                !authStatus.authenticated
                  ? 'opacity-50 cursor-not-allowed'
                  : 'cursor-pointer'
              } ${collapsed ? 'justify-center px-0' : ''}`}
              onClick={() => authStatus.authenticated && onToolChange(tool.id)}
              disabled={!authStatus.authenticated}
              title={collapsed ? tool.name : ''}
            >
              <IconComponent className={`flex-shrink-0 ${collapsed ? 'w-6 h-6' : 'w-5 h-5'}`} />
              {!collapsed && (
                <div className="flex flex-col items-start flex-1 min-w-0">
                  <span className="text-sm font-semibold">{tool.name}</span>
                  <span className={`text-xs truncate w-full ${isActive ? 'text-primary-100' : 'text-gray-500'}`}>
                    {tool.description}
                  </span>
                </div>
              )}
            </button>
          )
        })}
      </nav>
    </div>
  )
}

export default Sidebar
