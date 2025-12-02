import { useTranslation } from 'react-i18next'

function LanguageSelector() {
  const { i18n } = useTranslation()

  const languages = [
    { code: 'en', flag: '🇺🇸', label: 'English' },
    { code: 'es', flag: '🇪🇸', label: 'Español' },
    { code: 'pt', flag: '🇧🇷', label: 'Português' }
  ]

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng)
  }

  return (
    <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-1">
      {languages.map((lang) => (
        <button
          key={lang.code}
          onClick={() => changeLanguage(lang.code)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all text-sm font-medium ${
            i18n.language === lang.code
              ? 'bg-white text-primary-600 shadow-sm'
              : 'text-white hover:bg-white/10'
          }`}
          title={lang.label}
        >
          <span className="text-lg">{lang.flag}</span>
        </button>
      ))}
    </div>
  )
}

export default LanguageSelector
