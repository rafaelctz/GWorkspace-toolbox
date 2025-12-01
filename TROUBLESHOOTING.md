# DEA Toolbox - Troubleshooting Guide

## Credentials Upload Issues

### Error: "Invalid OAuth credentials format"

**Problem**: You're trying to upload the wrong type of Google Cloud credential file.

**Solution**: You need an **OAuth 2.0 Client ID** credential (Desktop app type), not a Service Account credential.

#### Step-by-Step: Getting the Correct Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Select or Create a Project**
   - Click the project dropdown at the top
   - Select existing project or create a new one

3. **Enable Admin SDK API**
   - Go to "APIs & Services" > "Library"
   - Search for "Admin SDK API"
   - Click "Enable" (if not already enabled)

4. **Create OAuth 2.0 Credentials** (IMPORTANT!)
   - Go to "APIs & Services" > "Credentials"
   - Click "**+ CREATE CREDENTIALS**"
   - Select "**OAuth client ID**" (NOT "Service account"!)

5. **Configure OAuth Consent Screen** (if prompted)
   - User Type: **Internal** (for Google Workspace) or **External**
   - App name: `DEA Toolbox`
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Add scope: `https://www.googleapis.com/auth/admin.directory.user.readonly`
   - Click "Save and Continue"

6. **Create the OAuth Client**
   - Application type: **Desktop app** ⚠️ (This is crucial!)
   - Name: `DEA Toolbox Desktop Client`
   - Click "**Create**"

7. **Download the Credentials**
   - A dialog will appear with your Client ID and Secret
   - Click "**DOWNLOAD JSON**"
   - Save this file (it will be named something like `client_secret_xxxxx.json`)

8. **Upload to DEA Toolbox**
   - Use this downloaded JSON file in the application

### What the Correct File Looks Like

**✅ CORRECT - OAuth 2.0 Client ID (Desktop app)**
```json
{
  "installed": {
    "client_id": "xxxxx.apps.googleusercontent.com",
    "project_id": "your-project",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "xxxxx",
    "redirect_uris": ["http://localhost"]
  }
}
```

OR (if you selected "Web application")

```json
{
  "web": {
    "client_id": "xxxxx.apps.googleusercontent.com",
    "project_id": "your-project",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "xxxxx"
  }
}
```

**❌ WRONG - Service Account (Will NOT work)**
```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "xxxxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "xxxxx@xxxxx.iam.gserviceaccount.com"
}
```

### Error: "Invalid JSON file"

**Problem**: The file is corrupted or not valid JSON.

**Solutions**:
- Re-download the credentials from Google Cloud Console
- Ensure you didn't edit the file
- Ensure the file wasn't corrupted during download
- Open the file in a text editor to verify it's valid JSON

### Error: "This is a Service Account credential"

**Problem**: You downloaded a Service Account JSON instead of OAuth 2.0 credentials.

**Solution**:
1. Go back to Google Cloud Console
2. Go to "APIs & Services" > "Credentials"
3. Instead of creating a "Service account", create an "OAuth client ID"
4. Choose "Desktop app" as the application type
5. Download the new credentials file

## Authentication Issues

### Error: "Authentication failed"

**Possible Causes & Solutions**:

1. **Admin SDK API Not Enabled**
   - Go to Google Cloud Console > APIs & Services > Library
   - Search "Admin SDK API"
   - Click "Enable"

2. **Not Using Admin Account**
   - You must authenticate with a Google Workspace **Super Admin** account
   - Regular users cannot access the Directory API

3. **OAuth Consent Screen Not Configured**
   - Ensure the OAuth consent screen is properly set up
   - Add the required scope: `https://www.googleapis.com/auth/admin.directory.user.readonly`

4. **Domain Not Using Google Workspace**
   - This tool only works with Google Workspace domains
   - Free Gmail accounts (@gmail.com) do not have access to Admin SDK

### Error: "403 Forbidden" or "Insufficient permissions"

**Problem**: The authenticated user doesn't have admin privileges.

**Solution**:
- Log out of the application
- Authenticate with a Google Workspace Super Admin account
- Regular users or limited admins cannot access user directory data

## Extraction Issues

### Error: "Not authenticated. Please authenticate first"

**Problem**: Your authentication session has expired or wasn't completed.

**Solution**:
1. Click "Logout" if you see it
2. Upload credentials again (if needed)
3. Click "Authenticate"
4. Complete the OAuth flow in the browser
5. Try the extraction again

### No Users Found / Empty CSV

**Possible Causes**:

1. **Domain Has No Users with Aliases**
   - The tool only extracts users who have email aliases
   - If no users have aliases configured, the CSV will be empty

2. **API Rate Limiting**
   - If you have a very large domain, you might hit rate limits
   - Wait a few minutes and try again

3. **Incorrect Domain**
   - Verify you're authenticated with the correct Google Workspace domain
   - Check the domain shown after authentication

## Docker Issues

### Containers Won't Start

**Check Port Conflicts**:
```bash
# Check if ports are in use
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# Or on Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

**Solution**: Stop other services using these ports or modify [docker-compose.yml](docker-compose.yml)

### Backend Container Crashes

**Check Logs**:
```bash
docker-compose logs backend
```

**Common Issues**:
- Missing Python dependencies: Rebuild with `docker-compose build --no-cache`
- Permission issues with volumes: Check file permissions
- Invalid environment variables: Check `.env` file

### Frontend Can't Reach Backend

**Problem**: Frontend shows network errors.

**Solutions**:
1. Ensure both containers are running: `docker-compose ps`
2. Check network configuration in [docker-compose.yml](docker-compose.yml)
3. Verify CORS settings in backend `.env`
4. Check browser console for detailed error messages

## Local Development Issues

### Backend Won't Start

**Check Python Version**:
```bash
python3 --version  # Should be 3.11 or higher
```

**Check Virtual Environment**:
```bash
cd backend
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

**Check Port 8000**:
```bash
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Frontend Won't Start

**Check Node.js Version**:
```bash
node --version  # Should be 18 or higher
npm --version
```

**Clear and Reinstall**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Frontend Can't Connect to Backend

**Check Backend is Running**:
```bash
curl http://localhost:8000/
# Should return: {"message":"DEA Toolbox API","version":"1.0.0","status":"running"}
```

**Check CORS Configuration**:
- Edit `backend/.env`
- Ensure `CORS_ORIGINS` includes your frontend URL
- Restart backend after changes

## Browser Issues

### OAuth Popup Blocked

**Solution**:
- Allow popups for localhost in your browser settings
- Manually open the authentication URL if needed

### Cookie/CORS Errors

**Solutions**:
1. Clear browser cache and cookies
2. Try in incognito/private mode
3. Check browser console for specific errors
4. Ensure backend CORS is configured correctly

## Still Having Issues?

### Collect Debug Information

1. **Backend Logs**:
   ```bash
   # Docker
   docker-compose logs backend

   # Local
   # Check terminal where backend is running
   ```

2. **Browser Console**:
   - Open Developer Tools (F12)
   - Check Console tab for errors
   - Check Network tab for failed requests

3. **Check API Directly**:
   ```bash
   # Test backend is running
   curl http://localhost:8000/

   # Check API docs
   # Visit: http://localhost:8000/docs
   ```

### Get Help

- Review the [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Check Google Cloud Console for API quotas and limits
- Verify all prerequisites are met
- Create an issue on the project repository with:
  - Error messages
  - Steps to reproduce
  - Environment details (OS, Python version, Node version)
  - Screenshots if applicable
