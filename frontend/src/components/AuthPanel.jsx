import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import './AuthPanel.css'

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
      <div className="card">
        <div className="loading">
          <div className="spinner"></div>
          <span>{t('common.loading')}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="card auth-panel">
      <h2>{t('auth.title')}</h2>

      <div className={`status-badge ${authStatus.authenticated ? 'authenticated' : 'not-authenticated'}`}>
        <span className="status-indicator"></span>
        {authStatus.authenticated ? t('auth.authenticated') : t('auth.notAuthenticated')}
      </div>

      {message.text && (
        <div className={`alert alert-${message.type}`}>
          {message.text}
        </div>
      )}

      {authStatus.authenticated ? (
        <>
          <div className="info-grid">
            <div className="info-item">
              <div className="info-label">{t('auth.adminEmail')}</div>
              <div className="info-value">{authStatus.adminEmail}</div>
            </div>
            <div className="info-item">
              <div className="info-label">{t('auth.domain')}</div>
              <div className="info-value">{authStatus.domain}</div>
            </div>
          </div>

          <div className="btn-group">
            <button onClick={handleLogout} className="btn btn-danger">
              {t('auth.logout')}
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="form-group">
            <label className="form-label">{t('auth.uploadCredentials')}</label>
            <p className="form-description">{t('auth.uploadCredentialsDesc')}</p>

            {!checkingCredentials && (
              <div className={`credentials-status ${credentialsExist ? 'exists' : 'not-exists'}`}>
                {credentialsExist ? (
                  <>
                    <span>{t('auth.credentialsUploaded')}</span>
                    <button
                      onClick={handleClearCredentials}
                      className="btn-link"
                      style={{ marginLeft: '1rem', color: 'var(--error-color)', cursor: 'pointer' }}
                    >
                      {t('auth.clearCredentials')}
                    </button>
                  </>
                ) : (
                  <span>{t('auth.noCredentials')}</span>
                )}
              </div>
            )}

            <div className="file-input-wrapper">
              <input
                type="file"
                id="credentials-file"
                accept=".json"
                onChange={handleFileSelect}
              />
              <label htmlFor="credentials-file" className="file-input-label">
                {t('auth.chooseFile')}
              </label>
              {selectedFile && (
                <span className="file-name">{selectedFile.name}</span>
              )}
            </div>

            {selectedFile && (
              <button
                onClick={handleUploadCredentials}
                disabled={uploading}
                className="btn btn-primary"
                style={{ marginTop: '1rem' }}
              >
                {uploading ? t('auth.uploadingCredentials') : t('auth.uploadCredentials')}
              </button>
            )}
          </div>

          {credentialType && credentialsExist && credentialType === 'service_account' && serviceAccountEmail && (
            <div className="form-group">
              <label className="form-label">{t('auth.serviceAccountInfo')}</label>
              <div className="info-value" style={{ padding: '0.75rem', background: 'var(--background)', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                {serviceAccountEmail}
              </div>
            </div>
          )}

          {credentialType === 'service_account' && (
            <div className="form-group">
              <label className="form-label">{t('auth.delegatedEmail')}</label>
              <p className="form-description">{t('auth.delegatedEmailDesc')}</p>
              <input
                type="email"
                value={delegatedEmail}
                onChange={(e) => setDelegatedEmail(e.target.value)}
                placeholder={t('auth.delegatedEmailPlaceholder')}
                className="text-input"
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  border: '1px solid var(--border-color)',
                  borderRadius: '4px',
                  fontSize: '0.875rem'
                }}
              />
            </div>
          )}

          <div className="form-group">
            <div className="btn-group">
              <button
                onClick={credentialType === 'service_account' ? handleServiceAccountAuth : handleAuthenticate}
                disabled={authenticating || (credentialType === 'service_account' && !delegatedEmail)}
                className="btn btn-primary"
              >
                {authenticating ? t('auth.authenticating') :
                 (credentialType === 'service_account' ? t('auth.serviceAccountAuth') : t('auth.authenticate'))}
              </button>
              {authenticating && (
                <button
                  onClick={() => {
                    setAuthenticating(false)
                    setMessage({ type: 'warning', text: 'Authentication cancelled. You can try again.' })
                  }}
                  className="btn btn-danger"
                >
                  Cancel
                </button>
              )}
            </div>
            {authenticating && credentialType === 'oauth' && (
              <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                A browser window should open for authentication. If it doesn't, please check for popup blockers.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default AuthPanel
