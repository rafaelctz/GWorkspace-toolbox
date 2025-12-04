# GWorkspace Toolbox

[![Docker Build](https://github.com/rafaelctz/GWorkspace-toolbox/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/rafaelctz/GWorkspace-toolbox/actions/workflows/docker-publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A comprehensive, open-source toolkit for Google Workspace administrators with tools for user management, group synchronization, and attribute injection.

**🚀 Features automatic updates • 🌍 Multi-language support • 🐳 Docker-ready • 🔒 Branch-protected**

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

We welcome contributions from the community! 🎉

### 🐛 Found a Bug?
[Open an issue](https://github.com/rafaelctz/GWorkspace-toolbox/issues/new) with details about the problem.

### 💡 Have an idea?
[Submit a feature request](https://github.com/rafaelctz/GWorkspace-toolbox/issues/new) or start a discussion.

### 🔨 Want to contribute code?
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Push to your branch (`git push origin feature/amazing-feature`)
5. [Open a Pull Request](https://github.com/rafaelctz/GWorkspace-toolbox/compare)

**Note:** The `main` branch is protected and requires:
- ✅ Pull Request review and approval
- ✅ CI/CD checks to pass (Docker builds)
- ✅ No direct pushes allowed

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration:
- ✅ Automatic Docker image builds on every push to `main`
- ✅ Images published to GitHub Container Registry
- ✅ Watchtower automatically updates running instances
- ✅ Branch protection ensures code quality

View builds: [GitHub Actions](https://github.com/rafaelctz/GWorkspace-toolbox/actions)

## Community & Support

- 📫 [Report Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- 💬 [Discussions](https://github.com/rafaelctz/GWorkspace-toolbox/discussions)
- 📖 [Documentation](https://github.com/rafaelctz/GWorkspace-toolbox/wiki)

## License

MIT License - see [LICENSE](LICENSE) for details

---

**Made with ❤️ for Google Workspace administrators**
