# Contributing to GWorkspace Toolbox

Thank you for your interest in contributing to GWorkspace Toolbox! This document provides guidelines and information for contributors.

## Project Vision

GWorkspace Toolbox aims to be a comprehensive suite of tools for Google Workspace administrators to manage users, groups, and organizational units. We're building practical, easy-to-use tools that solve real-world problems.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, browser, Docker version, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:
- Clear description of the proposed feature
- Use case: What problem does it solve?
- Any relevant examples or mockups

### Code Contributions

**Important:** The `main` branch is protected. Direct pushes are not allowed. All changes must go through Pull Requests with review approval.

#### Step-by-Step Process:

1. **Fork the repository**
   - Click "Fork" at the top of the repository page
   - Clone your fork: `git clone https://github.com/YOUR_USERNAME/GWorkspace-toolbox.git`

2. **Set up development environment**
   ```bash
   # Option 1: Local development
   cd backend && pip install -r requirements.txt
   cd ../frontend && npm install

   # Option 2: Docker development
   docker-compose -f docker-compose.dev.yml up
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation as needed
   - Write meaningful commit messages

5. **Test your changes**
   - Test locally before submitting
   - Ensure both backend and frontend work correctly
   - Test in both development and Docker environments
   - Verify CI/CD will pass (Docker builds)

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

   Use conventional commit prefixes:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code restructuring

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to the [repository](https://github.com/rafaelctz/GWorkspace-toolbox)
   - Click "Compare & pull request"
   - Fill out the PR template with:
     - Clear description of changes
     - Reference to related issues (`Fixes #123`)
     - Screenshots for UI changes
     - Test results/evidence

9. **Wait for CI/CD checks**
   - GitHub Actions will automatically build Docker images
   - Ensure all checks pass (green ✅)
   - Fix any issues if checks fail (red ❌)

10. **Code Review**
    - A maintainer will review your PR
    - Address any feedback or requested changes
    - Once approved, your PR will be merged!

11. **Celebrate!** 🎉
    - Your contribution is now part of the project
    - It will be automatically deployed via Watchtower

## Development Guidelines

### Backend (Python/FastAPI)

- Use type hints
- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Handle errors gracefully with appropriate HTTP status codes
- Use environment variables for configuration

### Frontend (React)

- Use functional components with hooks
- Keep components small and focused
- Use meaningful variable and function names
- Implement proper error handling
- Ensure responsive design

### i18n (Internationalization)

When adding new text:
1. Add the key to all three language files (`en.json`, `es.json`, `pt.json`)
2. Use the `useTranslation` hook in React components
3. Keep translations concise and clear

### Docker

- Keep images small
- Use multi-stage builds when appropriate
- Document any new environment variables

## Project Structure

```
GWorkspace-toolbox/
├── .github/
│   └── workflows/
│       └── docker-publish.yml   # CI/CD pipeline
├── backend/                     # FastAPI backend
│   ├── main.py                 # Main application
│   ├── services/               # Business logic
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Backend container
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── locales/            # i18n translations (en, es, pt)
│   │   └── App.jsx             # Main app component
│   ├── package.json            # Node dependencies
│   └── Dockerfile              # Frontend container
├── docker-compose.yml           # Production (pre-built images + Watchtower)
├── docker-compose.dev.yml       # Development (build from source)
├── README.md                    # Main documentation
├── CONTRIBUTING.md              # This file
└── LICENSE                      # MIT License
```

## Adding New Tools

When adding a new tool to the toolbox:

1. **Backend**:
   - Create a new service in `backend/services/`
   - Add API endpoints in `backend/main.py`
   - Update API documentation

2. **Frontend**:
   - Create a new component in `frontend/src/components/`
   - Add it to the ToolsPanel
   - Add translations to all language files

3. **Documentation**:
   - Update README.md
   - Update SETUP_GUIDE.md if needed
   - Add usage examples

## Code Review Process

All submissions require review and approval before merging. This is enforced by branch protection rules.

### What We Review:

- ✅ **Code Quality**: Clean, readable, well-structured code
- ✅ **Style Compliance**: Follows project conventions (PEP 8, React best practices)
- ✅ **Functionality**: Works as intended, no regressions
- ✅ **Tests**: Changes are tested and don't break existing features
- ✅ **Documentation**: README, comments, and docstrings updated
- ✅ **Security**: No credential leaks, proper input validation
- ✅ **CI/CD**: GitHub Actions checks pass (Docker builds)

### Review Timeline:

- Most PRs reviewed within **1-3 days**
- Simple fixes: often same day
- Large features: may take longer

### Automated Checks:

All PRs trigger automatic checks:
1. **Docker Backend Build**: Ensures backend Dockerfile builds successfully
2. **Docker Frontend Build**: Ensures frontend Dockerfile builds successfully

If checks fail:
- ❌ PR cannot be merged
- Review the GitHub Actions logs
- Fix issues and push updates
- Checks will run again automatically

### Getting Your PR Merged:

1. All CI/CD checks must pass ✅
2. At least 1 approval from a maintainer ✅
3. All review comments addressed ✅
4. No merge conflicts ✅

Once approved, a maintainer will merge using **squash merge** to keep history clean.

## Future Tools Roadmap

Ideas for future tools (contributions welcome!):
- **SAML Attribute Mapper**: Map user attributes for SAML apps
- **SSO Configuration Validator**: Verify SSO setup correctness
- **User Provisioning Checker**: Audit user provisioning status
- **License Assignment Reporter**: Track license usage
- **Group Membership Analyzer**: Analyze group hierarchies
- **Multi-provider Support**: Azure AD, Okta, OneLogin, etc.

## Code of Conduct

### Our Standards

We are committed to providing a welcoming and inclusive environment for everyone. We expect:

- ✅ **Respectful communication**: Be kind and professional
- ✅ **Constructive feedback**: Focus on code, not people
- ✅ **Collaboration**: Work together to solve problems
- ✅ **Patience**: Remember that everyone was a beginner once
- ✅ **Inclusivity**: Welcome contributors of all skill levels

### Unacceptable Behavior

- ❌ Harassment, discrimination, or offensive comments
- ❌ Personal attacks or trolling
- ❌ Spam or off-topic discussions
- ❌ Sharing others' private information

### Enforcement

Violations may result in:
1. Warning
2. Temporary ban from the project
3. Permanent ban for serious or repeated violations

Report issues to the project maintainer via GitHub issues or email.

## Questions?

Feel free to:
- Create an [issue](https://github.com/rafaelctz/GWorkspace-toolbox/issues) for questions
- Start a [discussion](https://github.com/rafaelctz/GWorkspace-toolbox/discussions)
- Ask in your Pull Request

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
