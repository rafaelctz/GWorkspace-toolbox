# GWorkspace Toolbox - Setup Guide

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Docker and Docker Compose (for containerized deployment)
- Google Workspace Admin account

## Google Cloud Console Setup

Before using the GWorkspace Toolbox, you need to set up a Google Cloud project and enable the necessary APIs.

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "GWorkspace Toolbox")
5. Click "Create"

### Step 2: Enable Admin SDK API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Admin SDK API"
3. Click on it and click "Enable"

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: Internal (if using Google Workspace) or External
   - App name: GWorkspace Toolbox
   - User support email: Your email
   - Developer contact: Your email
   - Save and continue
4. Back to "Create OAuth client ID":
   - Application type: "Desktop app"
   - Name: GWorkspace Toolbox Desktop
   - Click "Create"
5. Download the JSON file
6. Save it (you'll upload this through the application interface)

### Step 4: Configure OAuth Consent Screen Scopes

1. Go to "APIs & Services" > "OAuth consent screen"
2. Click "Edit App"
3. In "Scopes", add the following scope:
   - `https://www.googleapis.com/auth/admin.directory.user.readonly`
4. Save and continue

## Installation Methods

### Method 1: Local Development

#### Backend Setup

```bash
cd backend
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate

pip install -r requirements.txt

# Copy and configure environment file
cp .env.example .env

# Start the backend server
python main.py
```

The backend will be available at: http://localhost:8000

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Frontend Setup

```bash
cd frontend
npm install

# Start the development server
npm run dev
```

The frontend will be available at: http://localhost:3000

### Method 2: Docker Deployment

This is the recommended method for production deployment or if you want a quick setup.

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## First Time Usage

### 1. Upload Google Credentials

1. Open the application in your browser (http://localhost:3000)
2. In the "Google Workspace Authentication" section
3. Click "Choose File" and select the credentials JSON file you downloaded earlier
4. Click "Upload Credentials"

### 2. Authenticate

1. Click the "Authenticate" button
2. A browser window will open asking you to sign in with your Google Workspace admin account
3. Grant the requested permissions
4. The browser will show a success message
5. Return to the application - you should now see your admin email and domain

### 3. Extract Aliases

1. Once authenticated, scroll to "Available Tools"
2. Click "Extract Aliases"
3. Wait for the extraction to complete
4. View the statistics (total users, users with aliases)
5. Click "Download CSV" to get your file

## CSV Output Format

The generated CSV file contains:
- Column 1: Current Email (primary email address)
- Column 2: Alias 1 (first alias if exists)
- Column 3: Alias 2 (second alias if exists)
- Column N: Alias N (additional aliases as needed)

Example:
```
Current Email,Alias 1,Alias 2,Alias 3
john.doe@company.com,jdoe@company.com,johnd@company.com,
jane.smith@company.com,jsmith@company.com,,
```

## Troubleshooting

### Issue: "Credentials file not found"
**Solution**: Make sure you've uploaded the credentials JSON file through the interface first.

### Issue: "Authentication failed"
**Solution**:
- Verify that the Admin SDK API is enabled in your Google Cloud project
- Check that your OAuth credentials are configured correctly
- Ensure you're using a Google Workspace admin account

### Issue: "403 Forbidden" or "Insufficient permissions"
**Solution**:
- Make sure you're logged in as a Google Workspace super admin
- Verify that the OAuth consent screen has the correct scopes

### Issue: Docker containers won't start
**Solution**:
- Check if ports 3000 and 8000 are available
- Run `docker-compose logs` to see error messages
- Make sure Docker Desktop is running

## Security Best Practices

1. **Never commit credentials**: The `.gitignore` file is configured to exclude `credentials.json` and `token.json`

2. **Use environment-specific credentials**: Create separate OAuth clients for development and production

3. **Rotate credentials regularly**: Periodically regenerate OAuth credentials

4. **Limit scope**: The application only requests read-only access to user directory

5. **Secure exports**: CSV files containing user data should be handled according to your organization's data protection policies

## Multi-Language Support

The application supports three languages:
- English (default)
- Spanish (Español)
- Portuguese (Português)

Use the language selector in the top-right corner to switch languages.

## Need Help?

If you encounter issues not covered in this guide:
1. Check the application logs
2. Review the API documentation at http://localhost:8000/docs
3. Create an issue on the project repository

## Next Steps

After successfully setting up and using the Alias Extractor tool, you can:
- Use the CSV data to audit email aliases
- Import the data into other systems
- Plan for future tools (coming soon):
  - SAML attribute mapper
  - SSO configuration validator
  - User provisioning checker
