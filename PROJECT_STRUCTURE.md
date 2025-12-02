# GWorkspace Toolbox - Project Structure

## Directory Tree

```
GWorkspace-toolbox/
│
├── backend/                          # Python FastAPI backend
│   ├── services/                     # Business logic services
│   │   ├── __init__.py
│   │   └── google_workspace.py      # Google Workspace API integration
│   ├── main.py                      # FastAPI application & routes
│   ├── requirements.txt             # Python dependencies
│   ├── .env                        # Environment configuration
│   ├── .env.example               # Example environment file
│   ├── Dockerfile                 # Backend Docker image
│   ├── credentials.json           # Google OAuth credentials (not in git)
│   ├── token.json                 # OAuth token (not in git)
│   └── exports/                   # Generated CSV files (not in git)
│
├── frontend/                        # React frontend application
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── AuthPanel.jsx     # Authentication interface
│   │   │   ├── AuthPanel.css
│   │   │   ├── ToolsPanel.jsx    # Tools interface
│   │   │   ├── ToolsPanel.css
│   │   │   ├── LanguageSelector.jsx
│   │   │   └── LanguageSelector.css
│   │   ├── locales/              # i18n translation files
│   │   │   ├── en.json          # English translations
│   │   │   ├── es.json          # Spanish translations
│   │   │   └── pt.json          # Portuguese translations
│   │   ├── App.jsx              # Main application component
│   │   ├── App.css              # Application styles
│   │   ├── main.jsx             # React entry point
│   │   ├── index.css            # Global styles
│   │   └── i18n.js              # i18n configuration
│   ├── public/                   # Static assets
│   ├── index.html               # HTML template
│   ├── package.json             # Node.js dependencies
│   ├── vite.config.js          # Vite configuration
│   ├── nginx.conf              # Nginx config for Docker
│   ├── .env.production         # Production environment
│   └── Dockerfile              # Frontend Docker image
│
├── docker-compose.yml             # Docker orchestration
├── .dockerignore                 # Docker ignore rules
├── .gitignore                   # Git ignore rules
│
├── README.md                    # Main project documentation
├── SETUP_GUIDE.md              # Detailed setup instructions
├── CONTRIBUTING.md             # Contribution guidelines
├── PROJECT_STRUCTURE.md        # This file
├── LICENSE                     # MIT License
│
├── start-dev.sh               # Development startup script (macOS/Linux)
└── start-dev.bat              # Development startup script (Windows)
```

## Component Descriptions

### Backend Components

#### `main.py`
FastAPI application with endpoints for:
- Authentication management
- Google Workspace integration
- Alias extraction
- File downloads

#### `services/google_workspace.py`
Service layer handling:
- OAuth 2.0 authentication flow
- Google Admin SDK API calls
- User directory queries
- CSV generation

### Frontend Components

#### `App.jsx`
Main application container managing:
- Authentication state
- API communication
- Layout and routing

#### `AuthPanel.jsx`
Handles authentication flow:
- Credential file upload
- OAuth authentication
- Login/logout actions
- Status display

#### `ToolsPanel.jsx`
Tools interface providing:
- Tool selection
- Execution controls
- Results display
- File downloads

#### `LanguageSelector.jsx`
Language switching component:
- English/Spanish/Portuguese selection
- Persistent language preference

### Configuration Files

#### Backend Configuration
- `.env` - Environment variables
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container image definition

#### Frontend Configuration
- `package.json` - NPM dependencies and scripts
- `vite.config.js` - Build tool configuration
- `nginx.conf` - Web server configuration for production

#### Docker Configuration
- `docker-compose.yml` - Multi-container orchestration
- Network configuration
- Volume mappings
- Environment variables

## Data Flow

```
User Browser
    ↓
Frontend (React on port 3000)
    ↓ HTTP/REST API
Backend (FastAPI on port 8000)
    ↓ OAuth 2.0
Google Workspace Admin SDK
    ↓
User Directory Data
    ↓
CSV File Generation
    ↓
Download to User
```

## Key Features by Location

### Authentication Flow
- **Frontend**: [AuthPanel.jsx](frontend/src/components/AuthPanel.jsx)
- **Backend**: [main.py](backend/main.py) `/api/auth/*` endpoints
- **Service**: [google_workspace.py](backend/services/google_workspace.py) `authenticate()`

### Alias Extraction
- **Frontend**: [ToolsPanel.jsx](frontend/src/components/ToolsPanel.jsx)
- **Backend**: [main.py](backend/main.py) `/api/tools/extract-aliases`
- **Service**: [google_workspace.py](backend/services/google_workspace.py) `extract_aliases_to_csv()`

### Internationalization
- **Config**: [i18n.js](frontend/src/i18n.js)
- **Translations**: [locales/](frontend/src/locales/)
- **Component**: [LanguageSelector.jsx](frontend/src/components/LanguageSelector.jsx)

## Adding New Features

### New Tool Checklist

1. **Backend Service** (`backend/services/`)
   - Create service class with business logic
   - Implement data processing
   - Generate outputs

2. **Backend API** (`backend/main.py`)
   - Add endpoint route
   - Define request/response models
   - Handle authentication

3. **Frontend Component** (`frontend/src/components/`)
   - Create tool component
   - Implement UI controls
   - Handle API calls
   - Display results

4. **Translations** (`frontend/src/locales/`)
   - Add English strings
   - Add Spanish translations
   - Add Portuguese translations

5. **Documentation**
   - Update README.md
   - Update SETUP_GUIDE.md
   - Add usage examples

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend Framework | React 18 | UI components |
| Build Tool | Vite 5 | Fast development & bundling |
| Styling | CSS3 | Responsive design |
| Internationalization | react-i18next | Multi-language support |
| Backend Framework | FastAPI | REST API server |
| Language | Python 3.11 | Backend logic |
| API Client | Google API Python Client | Google Workspace integration |
| Authentication | OAuth 2.0 | Secure Google API access |
| Web Server | Nginx (production) | Static file serving & proxy |
| Containerization | Docker | Deployment & isolation |
| Orchestration | Docker Compose | Multi-container management |

## Security Considerations

### Sensitive Files (Never Commit)
- `backend/credentials.json` - OAuth credentials
- `backend/token.json` - OAuth tokens
- `backend/exports/*.csv` - User data exports
- `.env` - Environment variables

### Protected Endpoints
All tool endpoints require authentication via Google OAuth 2.0

### CORS Configuration
Configured in `backend/main.py` to allow specific origins only

## Development Workflow

1. **Local Development**
   - Use `start-dev.sh` (macOS/Linux) or `start-dev.bat` (Windows)
   - Backend auto-reloads on changes
   - Frontend hot-reloads via Vite

2. **Docker Development**
   - Use `docker-compose up` for containerized environment
   - Volumes mounted for live code updates
   - Network isolation between services

3. **Production Deployment**
   - Build optimized Docker images
   - Use environment variables for configuration
   - Deploy with `docker-compose up -d`
