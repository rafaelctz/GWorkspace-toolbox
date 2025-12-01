import { useTranslation } from 'react-i18next'
import './Sidebar.css'

function Sidebar({ currentTool, onToolChange, authStatus }) {
  const { t } = useTranslation()

  const tools = [
    {
      id: 'alias-extractor',
      name: t('tools.aliasExtractor.title'),
      icon: '◉',
      description: t('tools.aliasExtractor.description')
    },
    {
      id: 'attribute-injector',
      name: t('tools.attributeInjector.title'),
      icon: '◉',
      description: t('tools.attributeInjector.description')
    }
  ]

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>{t('tools.title')}</h2>
      </div>

      {!authStatus.authenticated && (
        <div className="sidebar-warning">
          <span className="warning-icon">!</span>
          <p>{t('tools.authRequired')}</p>
        </div>
      )}

      <nav className="sidebar-nav">
        {tools.map(tool => (
          <button
            key={tool.id}
            className={`sidebar-item ${currentTool === tool.id ? 'active' : ''} ${!authStatus.authenticated ? 'disabled' : ''}`}
            onClick={() => authStatus.authenticated && onToolChange(tool.id)}
            disabled={!authStatus.authenticated}
          >
            <span className="sidebar-item-icon">{tool.icon}</span>
            <div className="sidebar-item-content">
              <span className="sidebar-item-name">{tool.name}</span>
              <span className="sidebar-item-desc">{tool.description}</span>
            </div>
          </button>
        ))}
      </nav>
    </div>
  )
}

export default Sidebar
