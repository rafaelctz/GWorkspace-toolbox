# GWorkspace Toolbox

A comprehensive toolkit for Google Workspace administrators with tools for user management, group synchronization, and attribute injection.

## Features

### Google Workspace Tools

#### 1. Alias Extractor
Extract all user accounts with email aliases from Google Workspace and export to CSV format.

**Output Format:**
- Current Email
- Alias 1
- Alias 2
- Alias 3
- (Additional aliases as needed)

## Supported Languages

- English
- Spanish (Español)
- Portuguese (Português)

## Deployment Options

### Local Development

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

#### Google Workspace API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Admin SDK API**
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the credentials JSON file
6. Upload it through the application interface

### Docker Deployment (Recommended)

Docker deployment includes **automatic updates** via Watchtower - you'll always have the latest version!

```bash
# Pull and run pre-built images
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

**What's included:**
- ✅ Pre-built, tested images from GitHub Container Registry
- ✅ Automatic updates (checks daily for new versions)
- ✅ Auto-cleanup of old images
- ✅ No manual updates needed!

**Manual update (if needed):**
```bash
docker-compose pull
docker-compose up -d
```

**For local development (build from source):**
```bash
docker-compose -f docker-compose.dev.yml up
```

## Architecture

```
GWorkspace-toolbox/
├── backend/          # FastAPI Python backend
├── frontend/         # React + Vite frontend
├── docker-compose.yml
└── README.md
```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Security Notes

- Never commit `credentials.json` or `token.json` files
- Store sensitive credentials securely
- Use environment variables for configuration
- The application runs locally to maintain credential security

## Contributing

This is an open-source project. Contributions are welcome!

## License

MIT License
