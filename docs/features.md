# Features Overview

GWorkspace Toolbox provides three powerful tools for Google Workspace administrators, each designed to solve specific administrative challenges.

## Feature Summary

| Feature | Purpose | Use Cases |
|---------|---------|-----------|
| [Alias Extractor](/features/alias-extractor) | Export all user aliases to CSV | Auditing, migrations, reporting |
| [Attribute Injector](/features/attribute-injector) | Batch inject attributes to OUs | Custom fields, department codes, tags |
| [OU Group Sync](/features/ou-group-sync) | Sync OU members to Google Groups | Automatic group management, permissions |

## Alias Extractor

Extract all email aliases from your Google Workspace domain and export them to a CSV file.

**Key Benefits:**
- Complete visibility of all email aliases
- Easy export for documentation or migration
- No manual work clicking through users
- Perfect for compliance audits

[Learn more →](/features/alias-extractor)

## Attribute Injector

Batch inject custom attributes to all users within an Organizational Unit.

**Key Benefits:**
- Update hundreds of users in seconds
- Apply consistent attributes across teams
- No need for manual user-by-user updates
- Supports any custom schema attributes

[Learn more →](/features/attribute-injector)

## OU Group Sync

Automatically synchronize users from an Organizational Unit to a Google Group with smart sync capabilities.

**Key Benefits:**
- Automatic group membership management
- Smart Sync preserves manually added members
- Schedule daily synchronization
- Reduce manual group maintenance

[Learn more →](/features/ou-group-sync)

## Common Capabilities

All features share these capabilities:

### Authentication
- Secure OAuth 2.0 authentication
- No password storage
- Automatic token refresh
- Per-session authentication

### Multi-Language Support
- Full interface in English, Spanish, and Portuguese
- Seamless language switching
- Localized error messages and notifications

### Modern Interface
- Clean, intuitive design
- Real-time status updates
- Progress indicators for long operations
- Mobile-responsive layout

### Error Handling
- Clear error messages
- Automatic retry for transient failures
- Detailed logging for troubleshooting
- Graceful degradation

## Technical Details

### Architecture
- React frontend with Tailwind CSS
- FastAPI Python backend
- Google Admin SDK integration
- SQLite database for sync schedules

### Deployment
- Single Docker image
- Docker Compose for easy setup
- Automatic updates via Watchtower
- Minimal resource requirements

### Security
- OAuth 2.0 with minimal scopes
- No credential storage in application
- Token encryption at rest
- HTTPS ready for production

## Getting Started

1. [Install GWorkspace Toolbox](/installation)
2. Follow the [Quick Start Guide](/quickstart)
3. Explore individual feature documentation

## Need Help?

- [FAQ](/faq)
- [Troubleshooting](/troubleshooting)
- [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
