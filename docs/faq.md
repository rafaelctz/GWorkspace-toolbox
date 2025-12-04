# Frequently Asked Questions

Common questions and answers about GWorkspace Toolbox.

## General

### What is GWorkspace Toolbox?

GWorkspace Toolbox is a free, open-source suite of tools designed to help Google Workspace administrators automate common administrative tasks like managing email aliases, user attributes, and group memberships.

### Is GWorkspace Toolbox free?

Yes, GWorkspace Toolbox is completely free and open source under the MIT License. There are no premium features or paid tiers.

### What Google Workspace edition do I need?

GWorkspace Toolbox works with all Google Workspace editions (Business Starter, Business Standard, Business Plus, Enterprise) as long as you have administrator access.

### Can I use this with a free Gmail account?

No, GWorkspace Toolbox requires a Google Workspace (formerly G Suite) domain with administrator access. It uses the Admin SDK API which is not available for personal Gmail accounts.

## Installation & Setup

### Do I need technical skills to install GWorkspace Toolbox?

Basic familiarity with Docker and command line is helpful, but the installation is straightforward. Follow the [Installation Guide](/installation) step-by-step.

### Can I run this on Windows?

Yes, GWorkspace Toolbox runs on Windows, macOS, and Linux using Docker Desktop.

### Do I need a server to run GWorkspace Toolbox?

No, you can run it on your local computer. However, for scheduled syncs to work continuously, you'll need a machine that stays running (local server, VPS, or cloud instance).

### What ports does GWorkspace Toolbox use?

By default, it uses port 8000. You can change this in the `docker-compose.yml` file if needed.

### Where is my data stored?

All data is stored locally:
- Authentication tokens: `token.json` file
- Sync schedules: SQLite database in `./database` directory
- CSV exports: `./exports` directory

No data is sent to external servers except Google's APIs.

## Authentication & Security

### Is my Google Workspace data safe?

Yes. GWorkspace Toolbox uses OAuth 2.0 authentication and only requests the minimum required permissions. Your credentials are stored locally and never transmitted to third parties.

### What permissions does GWorkspace Toolbox need?

The tool requests:
- Read access to directory users (for Alias Extractor, OU Group Sync)
- Write access to directory users (for Attribute Injector)
- Manage groups (for OU Group Sync)

### Can I revoke access?

Yes, you can revoke access at any time:
1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find GWorkspace Toolbox
3. Click "Remove Access"

### Do I need to be a super administrator?

Yes, most features require super administrator privileges. Some features may work with delegated admin roles that have appropriate permissions.

### How often do I need to re-authenticate?

Authentication tokens are automatically refreshed. You typically only need to authenticate once unless:
- You revoke access manually
- Token files are deleted
- More than 6 months have passed without use

## Features

### Can Alias Extractor export aliases for specific OUs only?

Currently, Alias Extractor exports aliases for all users in the domain. You can filter the CSV file afterward by primary email address to get specific OU users.

### Does Attribute Injector work with standard Google fields?

No, Attribute Injector only works with custom schema attributes. Standard fields like name, phone, or job title must be managed through the Admin Console.

### Can I sync multiple OUs to one group?

Yes, you can create multiple sync jobs that all target the same group. Use Smart Sync mode to ensure users from all OUs are added without removing each other.

### What happens if I delete a user from the OU?

- **Smart Sync**: User remains in the group
- **Full Sync**: User is removed from the group on next sync

### Can I sync groups to OUs (reverse direction)?

No, GWorkspace Toolbox only supports OU-to-Group synchronization, not the reverse direction.

## Troubleshooting

### The application won't start

Check:
1. Docker is running: `docker ps`
2. Port 8000 is not in use by another application
3. Docker Compose file is present
4. Run `docker-compose logs` to see error messages

### I can't authenticate

Ensure:
1. credentials.json file is in the project directory
2. OAuth client redirect URI includes `http://localhost:8000/oauth2callback`
3. Admin SDK API is enabled in Google Cloud Console
4. You're using an administrator account

### Changes aren't taking effect

- Refresh the browser page
- Check Docker logs: `docker-compose logs -f`
- Verify you're authenticated (green indicator)
- Ensure target OU/group exists

### Scheduled syncs aren't running

Verify:
1. Docker container is running: `docker ps`
2. Schedule is enabled in the UI
3. Database volume is persisted (check docker-compose.yml)
4. Check logs for errors: `docker-compose logs -f app`

## Updates & Maintenance

### How do I update GWorkspace Toolbox?

If using Watchtower (included in docker-compose.yml), updates are automatic. Manual update:

```bash
docker-compose pull
docker-compose up -d
```

### How often is GWorkspace Toolbox updated?

Updates are released as needed for bug fixes, security patches, and new features. Check [GitHub Releases](https://github.com/rafaelctz/GWorkspace-toolbox/releases) for changelog.

### Will updates break my configuration?

No, updates maintain backward compatibility. Your credentials, database, and exports are stored in persistent volumes and are not affected by updates.

### How do I backup my data?

Backup these directories:
- `./database` - Sync schedules
- `./exports` - CSV files
- `credentials.json` - OAuth client credentials
- `token.json` - Authentication tokens

## Performance

### How many users can GWorkspace Toolbox handle?

GWorkspace Toolbox has been tested with domains up to 10,000 users. Performance depends on:
- Number of users in OU
- Google API rate limits
- Server resources

### Why is extraction/sync taking so long?

Google Workspace API has rate limits. For large domains:
- Operations are automatically throttled to comply with limits
- Failed requests are retried
- This is normal and expected

### Can I run multiple operations simultaneously?

Yes, you can run different features simultaneously (e.g., extract aliases while syncing groups). However, multiple operations on the same resource may cause conflicts.

## Contributing

### Can I contribute to GWorkspace Toolbox?

Yes! GWorkspace Toolbox is open source. See the [Contributing Guide](https://github.com/rafaelctz/GWorkspace-toolbox/blob/main/CONTRIBUTING.md) for details.

### I found a bug, how do I report it?

Please open an issue on [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues) with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Log output if applicable

### Can I request new features?

Absolutely! Open a feature request on [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues) and describe your use case.

## Still Have Questions?

- Check the [Troubleshooting Guide](/troubleshooting)
- Search [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Open a new issue if your question isn't answered
