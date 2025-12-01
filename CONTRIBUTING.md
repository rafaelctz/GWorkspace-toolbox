# Contributing to DEA Toolbox

Thank you for your interest in contributing to DEA Toolbox! This document provides guidelines and information for contributors.

## Project Vision

DEA Toolbox aims to be a comprehensive suite of tools for Active Directory administrators to manage SAML application integrations and SSO provider solutions. We're building practical, easy-to-use tools that solve real-world problems.

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

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation as needed

4. **Test your changes**
   - Test locally before submitting
   - Ensure both backend and frontend work correctly
   - Test in both development and Docker environments

5. **Commit your changes**
   ```bash
   git commit -m "Add: Brief description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Include screenshots for UI changes

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
DEA-toolbox/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application
│   ├── services/        # Business logic
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── locales/     # i18n translations
│   │   └── App.jsx      # Main app component
│   └── package.json     # Node dependencies
└── docker-compose.yml   # Docker configuration
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

All submissions require review. We'll:
- Review code quality and style
- Test functionality
- Check documentation
- Provide constructive feedback

## Future Tools Roadmap

Ideas for future tools (contributions welcome!):
- **SAML Attribute Mapper**: Map user attributes for SAML apps
- **SSO Configuration Validator**: Verify SSO setup correctness
- **User Provisioning Checker**: Audit user provisioning status
- **License Assignment Reporter**: Track license usage
- **Group Membership Analyzer**: Analyze group hierarchies
- **Multi-provider Support**: Azure AD, Okta, OneLogin, etc.

## Questions?

Feel free to create an issue for questions or discussions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
