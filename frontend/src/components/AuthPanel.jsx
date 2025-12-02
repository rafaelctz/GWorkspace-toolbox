import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { CheckCircle2, XCircle, Upload, LogOut, Key, Loader2, FileText, Trash2 } from 'lucide-react'

function AuthPanel({ authStatus, onAuthChange, apiBaseUrl }) {
  const { t } = useTranslation()
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [authenticating, setAuthenticating] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [credentialsExist, setCredentialsExist] = useState(false)
  const [checkingCredentials, setCheckingCredentials] = useState(true)
  const [credentialType, setCredentialType] = useState(null) // 'oauth' or 'service_account'
  const [serviceAccountEmail, setServiceAccountEmail] = useState('')
  const [delegatedEmail, setDelegatedEmail] = useState('')

  useEffect(() => {
    checkCredentialsStatus()
    checkCredentialType()
  }, [])

  const checkCredentialsStatus = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/auth/credentials-status`)
      setCredentialsExist(response.data.exists)
    } catch (error) {
      console.error('Failed to check credentials status:', error)
      setCredentialsExist(false)
    } finally {
      setCheckingCredentials(false)
    }
  }

  const checkCredentialType = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/auth/credential-type`)
      if (response.data.type) {
        setCredentialType(response.data.type)
        if (response.data.service_account_email) {
          setServiceAccountEmail(response.data.service_account_email)
        }
      }
    } catch (error) {
      console.error('Failed to check credential type:', error)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setMessage({ type: '', text: '' })
    }
  }

  const handleUploadCredentials = async () => {
    if (!selectedFile) return

    setUploading(true)
    setMessage({ type: '', text: '' })

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      await axios.post(`${apiBaseUrl}/api/auth/upload-credentials`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setMessage({ type: 'success', text: t('auth.uploadSuccess') })
      setSelectedFile(null)
      setCredentialsExist(true)
      // Check credential type after upload
      await checkCredentialType()
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || t('auth.uploadError')
      })
    } finally {
      setUploading(false)
    }
  }

  const handleAuthenticate = async () => {
    setAuthenticating(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await axios.post(`${apiBaseUrl}/api/auth/authenticate`, {}, {
        timeout: 120000 // 2 minute timeout
      })
      setMessage({ type: 'success', text: t('auth.authSuccess') })
      await onAuthChange()
    } catch (error) {
      console.error('Authentication error:', error)

      let errorMessage = t('auth.authError')

      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Authentication timed out. Please try again.'
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.message) {
        errorMessage = error.message
      }

      setMessage({
        type: 'error',
        text: errorMessage
      })
    } finally {
      setAuthenticating(false)
    }
  }

  const handleLogout = async () => {
    try {
      await axios.post(`${apiBaseUrl}/api/auth/logout`)
      onAuthChange()
      setMessage({ type: '', text: '' })
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Logout failed'
      })
    }
  }

  const handleServiceAccountAuth = async () => {
    if (!delegatedEmail) {
      setMessage({
        type: 'error',
        text: 'Please enter a delegated admin email'
      })
      return
    }

    setAuthenticating(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await axios.post(`${apiBaseUrl}/api/auth/authenticate-service-account`, {
        delegated_email: delegatedEmail
      }, {
        timeout: 30000
      })
      setMessage({ type: 'success', text: t('auth.authSuccess') })
      await onAuthChange()
    } catch (error) {
      console.error('Service account authentication error:', error)

      let errorMessage = error.response?.data?.detail || t('auth.authError')

      setMessage({
        type: 'error',
        text: errorMessage
      })
    } finally {
      setAuthenticating(false)
    }
  }

  const handleClearCredentials = async () => {
    if (!confirm('Are you sure you want to clear the uploaded credentials? You will need to upload them again to authenticate.')) {
      return
    }

    try {
      await axios.delete(`${apiBaseUrl}/api/auth/credentials`)
      setMessage({ type: 'success', text: t('auth.clearSuccess') })
      setCredentialsExist(false)
      setSelectedFile(null)
      setCredentialType(null)
      setServiceAccountEmail('')
      setDelegatedEmail('')
      onAuthChange()
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || t('auth.clearError')
      })
    }
  }

  if (authStatus.loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center gap-3">
          <Loader2 className="w-5 h-5 animate-spin text-primary-600" />
          <span className="text-gray-600">{t('common.loading')}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">{t('auth.title')}</h2>

      <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full mb-4 ${
        authStatus.authenticated
          ? 'bg-green-100 text-green-800'
          : 'bg-gray-100 text-gray-800'
      }`}>
        {authStatus.authenticated ? (
          <CheckCircle2 className="w-4 h-4" />
        ) : (
          <XCircle className="w-4 h-4" />
        )}
        <span className="font-medium text-sm">
          {authStatus.authenticated ? t('auth.authenticated') : t('auth.notAuthenticated')}
        </span>
      </div>

      {message.text && (
        <div className={`mb-4 p-4 rounded-lg border ${
          message.type === 'success'
            ? 'bg-green-50 border-green-200 text-green-800'
            : message.type === 'error'
            ? 'bg-red-50 border-red-200 text-red-800'
            : 'bg-amber-50 border-amber-200 text-amber-800'
        }`}>
          {message.text}
        </div>
      )}

      {authStatus.authenticated ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="text-xs font-medium text-gray-500 uppercase mb-1">
                {t('auth.adminEmail')}
              </div>
              <div className="text-sm text-gray-900 font-medium">
                {authStatus.adminEmail}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="text-xs font-medium text-gray-500 uppercase mb-1">
                {t('auth.domain')}
              </div>
              <div className="text-sm text-gray-900 font-medium">
                {authStatus.domain}
              </div>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
          >
            <LogOut className="w-4 h-4" />
            {t('auth.logout')}
          </button>
        </>
      ) : (
        <>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('auth.uploadCredentials')}
            </label>
            <p className="text-sm text-gray-500 mb-3">
              {t('auth.uploadCredentialsDesc')}
            </p>

            {!checkingCredentials && (
              <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm mb-3 ${
                credentialsExist
                  ? 'bg-green-50 text-green-800'
                  : 'bg-gray-50 text-gray-600'
              }`}>
                {credentialsExist ? (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{t('auth.credentialsUploaded')}</span>
                    <button
                      onClick={handleClearCredentials}
                      className="ml-2 text-red-600 hover:text-red-700 font-medium"
                    >
                      {t('auth.clearCredentials')}
                    </button>
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4" />
                    <span>{t('auth.noCredentials')}</span>
                  </>
                )}
              </div>
            )}

            <div className="flex items-center gap-3">
              <label
                htmlFor="credentials-file"
                className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg cursor-pointer transition-colors font-medium"
              >
                <FileText className="w-4 h-4" />
                {t('auth.chooseFile')}
              </label>
              <input
                type="file"
                id="credentials-file"
                accept=".json"
                onChange={handleFileSelect}
                className="hidden"
              />
              {selectedFile && (
                <span className="text-sm text-gray-600 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  {selectedFile.name}
                </span>
              )}
            </div>

            {selectedFile && (
              <button
                onClick={handleUploadCredentials}
                disabled={uploading}
                className="inline-flex items-center gap-2 px-4 py-2 mt-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    {t('auth.uploadingCredentials')}
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    {t('auth.uploadCredentials')}
                  </>
                )}
              </button>
            )}
          </div>

          {credentialType && credentialsExist && credentialType === 'service_account' && serviceAccountEmail && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('auth.serviceAccountInfo')}
              </label>
              <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                <p className="text-sm text-blue-900 font-mono">{serviceAccountEmail}</p>
              </div>
            </div>
          )}

          {credentialType === 'service_account' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('auth.delegatedEmail')}
              </label>
              <p className="text-sm text-gray-500 mb-3">
                {t('auth.delegatedEmailDesc')}
              </p>
              <input
                type="email"
                value={delegatedEmail}
                onChange={(e) => setDelegatedEmail(e.target.value)}
                placeholder={t('auth.delegatedEmailPlaceholder')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              />
            </div>
          )}

          <div className="flex items-center gap-3">
            <button
              onClick={credentialType === 'service_account' ? handleServiceAccountAuth : handleAuthenticate}
              disabled={authenticating || (credentialType === 'service_account' && !delegatedEmail)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {authenticating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {t('auth.authenticating')}
                </>
              ) : (
                <>
                  <Key className="w-4 h-4" />
                  {credentialType === 'service_account' ? t('auth.serviceAccountAuth') : t('auth.authenticate')}
                </>
              )}
            </button>
            {authenticating && (
              <button
                onClick={() => {
                  setAuthenticating(false)
                  setMessage({ type: 'warning', text: 'Authentication cancelled. You can try again.' })
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                Cancel
              </button>
            )}
          </div>
          {authenticating && credentialType === 'oauth' && (
            <p className="mt-3 text-sm text-gray-500">
              A browser window should open for authentication. If it doesn't, please check for popup blockers.
            </p>
          )}
        </>
      )}
    </div>
  )
}

export default AuthPanel
