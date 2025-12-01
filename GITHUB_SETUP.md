# GitHub Setup Guide

## Repository Structure

This project uses a two-branch strategy:

- **main** - Advanced version with database, batch processing, async tasks, and progress tracking
- **light-version** - Simple, lightweight version with just the Alias Extractor and basic Attribute Injector

## Steps to Push to GitHub

### 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `DEA-toolbox` (or your preferred name)
3. Description: "Tools for Google Workspace administrators - SAML & SSO Integration Solutions"
4. Choose: Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### 2. Add GitHub Remote

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/DEA-toolbox.git
```

Or if using SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/DEA-toolbox.git
```

### 3. Push Both Branches

```bash
# Push main branch
git push -u origin main

# Push light-version branch
git push -u origin light-version
```

### 4. Set Default Branch (Optional)

On GitHub:
1. Go to Settings → Branches
2. Set default branch to `main` (or `light-version` if you prefer)

## Branch Usage

### Main Branch (Advanced Version)
```bash
git checkout main
```

This branch will contain:
- SQLite database for persistent storage
- Saved authentication credentials
- User caching system
- Batch processing with async execution
- Job queue with progress tracking
- Task history and results

**Use this for**: Production deployments requiring high volume processing

### Light Version Branch (Simple Version)
```bash
git checkout light-version
```

This branch contains:
- Simple file-based authentication
- Synchronous operations
- No database required
- Alias Extractor tool
- Basic Attribute Injector

**Use this for**: Quick deployments, testing, or simple use cases

## Development Workflow

### Working on Advanced Features (main branch)
```bash
git checkout main
git pull origin main
# Make changes
git add .
git commit -m "feat: your feature description"
git push origin main
```

### Backporting Simple Fixes to Light Version
If you fix a bug that applies to both versions:

```bash
# Fix on main first
git checkout main
# Make fix and commit
git commit -m "fix: bug description"

# Cherry-pick to light-version
git checkout light-version
git cherry-pick <commit-hash>
git push origin light-version
```

## Release Strategy

### Versioning
- **Light Version**: v1.x.x (simple, stable)
- **Main Version**: v2.x.x (advanced, feature-rich)

### Creating Releases

On GitHub:
1. Go to Releases → Create new release
2. Choose branch (main or light-version)
3. Tag version: `v1.0.0` or `v2.0.0`
4. Add release notes
5. Publish release

## Quick Reference

```bash
# Check current branch
git branch

# Switch branches
git checkout main              # Switch to advanced version
git checkout light-version     # Switch to simple version

# View differences between branches
git diff light-version main

# List all branches
git branch -a

# Show remote URL
git remote -v

# Pull latest changes
git pull origin main

# Push changes
git push origin main
```

## Deployment Notes

### Light Version Deployment
```bash
git checkout light-version
docker-compose up -d
```

### Main Version Deployment
```bash
git checkout main
# Database will be created automatically in data/
docker-compose up -d
```

## Troubleshooting

### If push is rejected
```bash
git pull --rebase origin main
git push origin main
```

### If you need to change remote URL
```bash
git remote set-url origin NEW_URL
```

### View commit history
```bash
git log --oneline --graph --all --decorate
```

---

**Repository Status**: ✅ Ready to push to GitHub
**Current Branch**: main
**Total Commits**: 1
**Branches**: 2 (main, light-version)
