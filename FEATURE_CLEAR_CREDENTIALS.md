# Clear Credentials Feature

## Overview
Added the ability to clear uploaded Google OAuth credentials through the UI, making it easy to switch credentials or start fresh when troubleshooting.

## Features

### 1. Credentials Status Display
- Shows ✅ "Credentials uploaded" when credentials exist
- Shows ℹ️ "No credentials uploaded" when no credentials

### 2. Clear Credentials Button
- 🗑️ "Clear Credentials" button appears when credentials exist
- Confirmation dialog before deletion
- Deletes both `credentials.json` and `token.json`
- Resets authentication state

### 3. Multi-language Support
- English, Spanish, and Portuguese translations
- All new UI text is localized

## New API Endpoints

### DELETE `/api/auth/credentials`
Deletes uploaded credentials and token files.

**Response:**
```json
{
  "message": "Credentials deleted successfully"
}
```

### GET `/api/auth/credentials-status`
Checks if credentials file exists.

**Response:**
```json
{
  "exists": true,
  "path": "./credentials.json"
}
```

## User Flow

1. **Upload Credentials**
   - User uploads OAuth JSON file
   - Status shows: ✅ "Credentials uploaded"
   - "Clear Credentials" link appears

2. **Clear Credentials**
   - User clicks 🗑️ "Clear Credentials"
   - Confirmation dialog appears
   - If confirmed:
     - Credentials deleted
     - Status shows: ℹ️ "No credentials uploaded"
     - Can upload new file

3. **Ready for New Upload**
   - File picker ready for new credentials
   - No need to restart application

## Files Modified

### Backend
- [backend/main.py](backend/main.py)
  - Added `delete_credentials()` endpoint
  - Added `credentials_status()` endpoint

### Frontend
- [frontend/src/components/AuthPanel.jsx](frontend/src/components/AuthPanel.jsx)
  - Added credentials status check
  - Added clear credentials function
  - Updated UI to show status and button

- [frontend/src/components/AuthPanel.css](frontend/src/components/AuthPanel.css)
  - Added styling for credentials status
  - Added styling for link button

### Translations
- [frontend/src/locales/en.json](frontend/src/locales/en.json)
- [frontend/src/locales/es.json](frontend/src/locales/es.json)
- [frontend/src/locales/pt.json](frontend/src/locales/pt.json)
  - Added: `clearCredentials`
  - Added: `credentialsUploaded`
  - Added: `noCredentials`
  - Added: `clearSuccess`
  - Added: `clearError`

## Usage

### Via UI
1. Open the application
2. Look for the credentials status under "Upload Credentials"
3. If credentials are uploaded, click "Clear Credentials"
4. Confirm the action
5. Upload new credentials

### Via API (for testing)
```bash
# Check credentials status
curl http://localhost:8000/api/auth/credentials-status

# Clear credentials
curl -X DELETE http://localhost:8000/api/auth/credentials
```

## Benefits

✅ **Easy Troubleshooting** - Quickly clear and re-upload credentials when testing
✅ **Switch Accounts** - Easy to change between different Google Workspace domains
✅ **Clean State** - Start fresh without restarting the application
✅ **Visual Feedback** - Always know if credentials are uploaded
✅ **Safe Operation** - Confirmation dialog prevents accidental deletion

## Screenshots

### Before Upload
```
ℹ️ No credentials uploaded
[Choose File] button
```

### After Upload
```
✅ Credentials uploaded   🗑️ Clear Credentials
[Choose File] button
```

## Testing

1. **Test Upload and Clear**
   ```bash
   # Start backend
   cd backend && python main.py

   # In another terminal, start frontend
   cd frontend && npm run dev

   # Open browser to http://localhost:3000
   # Upload credentials -> should see ✅ status
   # Click Clear Credentials -> should see ℹ️ status
   ```

2. **Test API Directly**
   ```bash
   # Check status
   curl http://localhost:8000/api/auth/credentials-status

   # Clear
   curl -X DELETE http://localhost:8000/api/auth/credentials

   # Verify cleared
   curl http://localhost:8000/api/auth/credentials-status
   # Should return: {"exists": false, "path": null}
   ```

## Error Handling

- **File doesn't exist**: Silently succeeds (idempotent operation)
- **Permission errors**: Returns 500 with error message
- **User cancels confirmation**: No action taken

## Security Notes

- Confirmation required before deletion
- Deletes both credentials and authentication token
- Resets global service instance
- Forces re-authentication if credentials are cleared
