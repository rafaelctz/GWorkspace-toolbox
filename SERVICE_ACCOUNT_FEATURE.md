# Service Account Authentication Feature

## Overview
Added support for Google Workspace Service Account authentication with domain-wide delegation as an alternative to OAuth 2.0. This allows delegated admin tasks without interactive login.

## Backend Changes ✅ COMPLETE

### Updated Files

#### 1. `backend/services/google_workspace.py`
- Added service account imports
- Auto-detection of credential type (OAuth vs Service Account)
- New `authenticate_service_account(delegated_email)` method
- Support for domain-wide delegation
- `auth_type` tracking ('oauth' or 'service_account')

#### 2. `backend/main.py`
**New Endpoints:**
- `POST /api/auth/authenticate-service-account` - Authenticate with service account
- `GET /api/auth/credential-type` - Detect uploaded credential type

### How It Works

1. **Credential Detection**
   - Automatically detects if uploaded file is OAuth or Service Account
   - Service Account: has `"type": "service_account"`
   - OAuth: has `"installed"` or `"web"` keys

2. **Service Account Auth Flow**
   - Upload service account JSON
   - Enter admin email to delegate to
   - Service account impersonates that admin
   - Full directory access with that admin's permissions

3. **Domain-Wide Delegation**
   - Service account must have domain-wide delegation enabled
   - Must be authorized for scope: `https://www.googleapis.com/auth/admin.directory.user.readonly`

## Frontend Changes ✅ COMPLETE

### What Was Added

1. **Detect credential type after upload** ✅
   - `checkCredentialType()` function calls `/api/auth/credential-type`
   - Updates `credentialType` state ('oauth' or 'service_account')

2. **Show appropriate auth UI based on type:** ✅
   - OAuth: Shows "Authenticate" button (opens browser)
   - Service Account: Shows "Delegated Admin Email" input + "Authenticate with Service Account" button
   - Conditional rendering based on `credentialType` state

3. **Translation updates:** ✅
   - Service account auth labels (EN/ES/PT)
   - Delegated email input fields
   - Service account-specific messages

## Usage

### For OAuth 2.0 (Super Admin - Interactive)
```
1. Upload OAuth Client credentials
2. Click "Authenticate"
3. Browser opens for login
4. Admin grants permission
5. Authenticated!
```

### For Service Account (Delegated - Non-Interactive)
```
1. Upload Service Account credentials
2. Enter delegated admin email (e.g., admin@company.com)
3. Click "Authenticate"
4. Authenticated! (no browser popup)
```

## Setup Requirements

### Service Account Setup

1. **Create Service Account** (Google Cloud Console)
   - Go to IAM & Admin > Service Accounts
   - Create service account
   - Download JSON key

2. **Enable Domain-Wide Delegation**
   - Edit service account
   - Enable "Enable Google Workspace Domain-wide Delegation"
   - Note the Client ID

3. **Authorize in Admin Console**
   - Go to Google Workspace Admin Console
   - Security > API Controls > Domain-wide Delegation
   - Add new:
     - Client ID: (from service account)
     - Scopes: `https://www.googleapis.com/auth/admin.directory.user.readonly`

4. **Use in DEA Toolbox**
   - Upload the service account JSON
   - Enter an admin email to impersonate
   - Authenticate!

## Benefits

✅ **No Interactive Login** - Perfect for automation
✅ **Delegated Access** - Service account acts as specified admin
✅ **Better for Scripts** - No token expiration issues
✅ **Multiple Admins** - Can delegate to different admins as needed
✅ **Secure** - No personal credentials needed

## API Examples

### Check Credential Type
```bash
curl http://localhost:8000/api/auth/credential-type
```

**Response (OAuth):**
```json
{
  "type": "oauth",
  "exists": true
}
```

**Response (Service Account):**
```json
{
  "type": "service_account",
  "exists": true,
  "service_account_email": "sa@project.iam.gserviceaccount.com"
}
```

### Authenticate with Service Account
```bash
curl -X POST http://localhost:8000/api/auth/authenticate-service-account \
  -H "Content-Type: application/json" \
  -d '{"delegated_email": "admin@company.com"}'
```

**Response:**
```json
{
  "message": "Service account authentication successful",
  "admin_email": "admin@company.com",
  "domain": "company.com",
  "auth_type": "service_account"
}
```

## Error Handling

### Common Errors

**"Domain-wide delegation not enabled"**
- Solution: Enable domain-wide delegation in service account settings

**"Service account not authorized"**
- Solution: Add service account Client ID to Admin Console > Domain-wide Delegation

**"Invalid delegated email"**
- Solution: Ensure email is a valid admin in the domain

## Security Considerations

1. **Service Account Keys** are sensitive - treat like passwords
2. **Domain-Wide Delegation** grants broad access - use carefully
3. **Rotate Keys** regularly
4. **Limit Scopes** to only what's needed
5. **Audit Usage** regularly in Admin Console

## Next Steps

1. ✅ Backend implementation complete
2. ✅ Frontend UI updates complete
3. ✅ Documentation updates complete
4. 🧪 Testing both auth flows (ready for testing)

## Testing

### Test OAuth Flow
1. Upload OAuth credentials
2. Should detect type: "oauth"
3. Authenticate button works as before

### Test Service Account Flow
1. Upload service account JSON
2. Should detect type: "service_account"
3. Enter admin email
4. Authenticate
5. Should show delegated admin email and domain

## Files Modified

- ✅ `backend/services/google_workspace.py`
- ✅ `backend/main.py`
- ✅ `frontend/src/components/AuthPanel.jsx`
- ✅ `frontend/src/locales/en.json`
- ✅ `frontend/src/locales/es.json`
- ✅ `frontend/src/locales/pt.json`
