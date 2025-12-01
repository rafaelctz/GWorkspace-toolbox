import { useTranslation } from 'react-i18next'
import './LanguageSelector.css'

function LanguageSelector() {
  const { i18n, t } = useTranslation()

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng)
  }

  return (
    <div className="language-selector">
      <label className="language-label">{t('language.label')}:</label>
      <select
        value={i18n.language}
        onChange={(e) => changeLanguage(e.target.value)}
        className="language-select"
      >
        <option value="en">{t('language.english')}</option>
        <option value="es">{t('language.spanish')}</option>
        <option value="pt">{t('language.portuguese')}</option>
      </select>
    </div>
  )
}

export default LanguageSelector
