# Installation

GWorkspace Toolbox runs as a Docker container, making installation simple and consistent across all platforms.

## Prerequisites

- Docker and Docker Compose installed on your system
- Google Workspace administrator account
- Google Cloud Project with Admin SDK API enabled

## Step 1: Install Docker

### Windows
Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

### macOS
Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)

### Linux
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## Step 2: Google Workspace Setup

### Enable Admin SDK API
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Navigate to **APIs & Services** > **Library**
4. Search for "Admin SDK API" and enable it

### Create OAuth 2.0 Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Select **Web application**
4. Add authorized redirect URI: `http://localhost:8000/oauth2callback`
5. Download the credentials JSON file

## Step 3: Deploy with Docker

### Create Project Directory
```bash
mkdir gworkspace-toolbox
cd gworkspace-toolbox
```

### Download Docker Compose Configuration
```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/rafaelctz/GWorkspace-toolbox/main/docker-compose.yml
```

### Add Your Credentials
1. Save your downloaded OAuth credentials as `credentials.json` in the project directory
2. The application will guide you through authentication on first run

### Start the Application
```bash
docker-compose up -d
```

The application will be available at `http://localhost:8000`

## Step 4: Initial Setup

1. Open your browser to `http://localhost:8000`
2. Click **Authenticate** button
3. Sign in with your Google Workspace admin account
4. Grant the requested permissions
5. You'll be redirected back to the application

## Automatic Updates

The Docker Compose configuration includes Watchtower, which automatically checks for updates daily and keeps your installation current.

To manually update:
```bash
docker-compose pull
docker-compose up -d
```

## Next Steps

Now that you're installed, check out the [Quick Start Guide](/quickstart) to learn how to use the features.

## Troubleshooting

If you encounter issues, see the [Troubleshooting Guide](/troubleshooting) or check [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues).
