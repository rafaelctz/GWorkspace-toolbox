# Troubleshooting Guide

Solutions to common problems when using GWorkspace Toolbox.

## Installation Issues

### Docker Not Starting

**Problem**: Docker container won't start or immediately exits.

**Solutions**:

```bash
# Check if Docker is running
docker ps

# View container logs
docker-compose logs app

# Check for port conflicts
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Restart containers
docker-compose down
docker-compose up -d
```

### Port Already in Use

**Problem**: Error message about port 8000 being in use.

**Solution**: Change the port in docker-compose.yml:

```yaml
services:
  app:
    ports:
      - "8080:8000"  # Use 8080 instead of 8000
```

Then access the app at `http://localhost:8080`

### Credentials File Not Found

**Problem**: Application can't find credentials.json.

**Solutions**:

```bash
# Check file exists
ls -la credentials.json

# Ensure it's in the project directory
pwd
ls

# Verify docker-compose.yml volume mount
cat docker-compose.yml | grep credentials
```

## Authentication Issues

### OAuth Error: redirect_uri_mismatch

**Problem**: OAuth error mentioning redirect URI mismatch.

**Solution**:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to APIs & Services > Credentials
3. Edit your OAuth 2.0 Client ID
4. Under "Authorized redirect URIs", add:
   - `http://localhost:8000/oauth2callback`
5. Save and try authenticating again

### Authentication Keeps Failing

**Problem**: Can't complete authentication flow.

**Checklist**:

- [ ] Admin SDK API is enabled in Google Cloud Console
- [ ] OAuth client redirect URI is configured correctly
- [ ] You're using an administrator account
- [ ] credentials.json is the OAuth client (not Service Account)
- [ ] Browser allows popups from localhost
- [ ] No browser extensions blocking the flow

**Reset authentication**:

```bash
# Stop containers
docker-compose down

# Remove token file
rm token.json

# Start containers
docker-compose up -d

# Try authenticating again
```

### Token Expired Errors

**Problem**: Error messages about expired tokens.

**Solution**: Delete the token file and re-authenticate:

```bash
docker-compose down
rm token.json
docker-compose up -d
```

Then authenticate again through the UI.

## Alias Extractor Issues

### No Aliases in CSV

**Problem**: CSV file is empty or missing aliases.

**Possible causes**:

1. **No aliases exist**: Check Admin Console to verify users have aliases
2. **Permission issue**: Ensure authenticated as admin
3. **API not enabled**: Verify Admin SDK API is enabled

**Debug steps**:

```bash
# Check container logs
docker-compose logs app | grep -i alias

# Verify authentication status
# Check for green indicator in UI

# Test API access in Google Cloud Console API Explorer
```

### Extraction Timeout

**Problem**: Extraction times out or never completes.

**Solutions**:

1. **For large domains** (1000+ users), extraction may take 5-10 minutes
2. Check Docker container logs for progress
3. Ensure stable internet connection
4. Increase Docker memory if needed:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G
```

## Attribute Injector Issues

### "Attribute not found" Error

**Problem**: Error saying attribute doesn't exist.

**Solution**:

1. Verify custom schema exists in Admin Console:
   - Directory > Users > Manage custom attributes
2. Check attribute name format: `SchemaName.fieldName`
3. Ensure exact case matching (case-sensitive)

**Example**:

```
✗ Wrong: employeeinfo.department
✗ Wrong: EmployeeInfo.Department
✓ Correct: EmployeeInfo.department
```

### "OU not found" Error

**Problem**: Error saying organizational unit doesn't exist.

**Solution**:

1. Verify OU path starts with `/`
2. Check exact path in Admin Console (case-sensitive)
3. No trailing spaces or special characters

**Examples**:

```
✗ Wrong: Sales/North America
✗ Wrong: /Sales/North America/  (trailing slash)
✓ Correct: /Sales/North America
```

### Permission Denied

**Problem**: Error about insufficient permissions.

**Solutions**:

1. Authenticate as super administrator
2. Or ensure delegated admin has user management permissions
3. Check OAuth scopes include user write permissions

### No Users Updated

**Problem**: Operation completes but reports 0 users updated.

**Possible causes**:

1. OU is empty - check Admin Console
2. OU path is incorrect
3. Tool doesn't recurse into sub-OUs by default

**Verify**:

```bash
# Check container logs
docker-compose logs app | grep -i inject
```

## OU Group Sync Issues

### "Group not found" Error

**Problem**: Error saying group doesn't exist.

**Solutions**:

1. Verify group email address is exactly correct
2. Check group exists in Admin Console or Gmail
3. Ensure you have permission to manage the group
4. Group email must be complete: `team@company.com`

**Test access**:

1. Try accessing the group in Gmail
2. Check if you're a group owner or manager
3. Verify group email in Admin Console

### Members Not Being Added

**Problem**: Sync completes but members aren't added to group.

**Checklist**:

- [ ] Group exists and is accessible
- [ ] OU contains users (not empty)
- [ ] You have permission to manage the group
- [ ] Users aren't already in the group
- [ ] API permissions are correct

**Debug**:

```bash
# Check logs for detailed error messages
docker-compose logs app | grep -i sync
```

### Members Unexpectedly Removed

**Problem**: Users were removed from the group after sync.

**Cause**: You're using **Full Sync** mode, which removes users not in the OU.

**Solutions**:

1. Switch to **Smart Sync** mode if you want to preserve manual members
2. Add removed users to the OU
3. Re-add them manually and use Smart Sync going forward

### Scheduled Sync Not Running

**Problem**: Scheduled sync jobs aren't executing.

**Checklist**:

- [ ] Docker container is running continuously
- [ ] Schedule toggle is enabled in UI
- [ ] Database volume is persisted
- [ ] No errors in container logs

**Debug**:

```bash
# Check if container is running
docker ps | grep gworkspace

# View logs
docker-compose logs -f app

# Check database file exists
ls -la database/

# Verify schedule in UI
# Go to OU Group Sync and check scheduled jobs list
```

**Reset schedule**:

```bash
# Stop containers
docker-compose down

# Check database volume
docker volume ls | grep gworkspace

# Restart
docker-compose up -d

# Recreate schedule in UI
```

## UI/Interface Issues

### Page Not Loading

**Problem**: Browser shows connection error or blank page.

**Solutions**:

```bash
# Check container is running
docker ps

# Check container health
docker-compose ps

# View logs for errors
docker-compose logs app

# Restart containers
docker-compose restart

# Verify URL
# Should be http://localhost:8000 (not https)
```

### Authentication Status Not Showing

**Problem**: Can't see authentication status or buttons.

**Solutions**:

1. Clear browser cache and cookies
2. Try a different browser
3. Check browser console for JavaScript errors (F12)
4. Ensure page fully loaded before interacting

### Language Not Changing

**Problem**: Language selector doesn't change the interface.

**Solutions**:

1. Refresh the page after selecting language
2. Clear browser cache
3. Check browser console for errors

## Docker Issues

### Container Keeps Restarting

**Problem**: Container enters a restart loop.

**Debug**:

```bash
# View logs to see error
docker-compose logs app

# Common causes:
# - Port conflict
# - Missing files (credentials.json)
# - Permission issues
# - Corrupted database

# Stop and inspect
docker-compose down
docker-compose up
# (without -d to see live output)
```

### Watchtower Not Updating

**Problem**: Watchtower isn't automatically updating the application.

**Check**:

```bash
# Verify Watchtower is running
docker ps | grep watchtower

# Check Watchtower logs
docker-compose logs watchtower

# Manually trigger update
docker-compose pull
docker-compose up -d
```

### Volume Permission Errors

**Problem**: Errors about file permissions in mounted volumes.

**Solutions**:

```bash
# Fix permissions on mounted directories
chmod -R 755 exports/
chmod -R 755 database/

# For credentials
chmod 600 credentials.json
chmod 600 token.json
```

## Performance Issues

### Slow API Responses

**Problem**: Operations take much longer than expected.

**Possible causes**:

1. **Google API rate limiting** (normal for large operations)
2. Slow internet connection
3. Google Workspace having issues

**Solutions**:

- Be patient with large domains (1000+ users)
- Check [Google Workspace Status Dashboard](https://www.google.com/appsstatus/)
- Operations will automatically retry and continue

### High Memory Usage

**Problem**: Docker container using excessive memory.

**Solutions**:

```yaml
# Add resource limits in docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

## API & Network Issues

### SSL Certificate Errors

**Problem**: SSL/TLS certificate errors when calling Google APIs.

**Solutions**:

```bash
# Usually caused by system time being wrong
# Check system time
date

# Synchronize system time
# macOS:
sudo sntp -sS time.apple.com

# Linux:
sudo ntpdate time.nist.gov
```

### Connection Timeout

**Problem**: Requests to Google APIs timing out.

**Checklist**:

- [ ] Internet connection is stable
- [ ] Firewall allows outbound HTTPS (port 443)
- [ ] Proxy settings if behind corporate firewall
- [ ] Google Workspace services are operational

## Database Issues

### Corrupted Database

**Problem**: Scheduled syncs not loading or database errors.

**Solution**: Reset the database:

```bash
# Backup current database
cp -r database/ database_backup/

# Stop containers
docker-compose down

# Remove database
rm -rf database/*

# Restart - will create fresh database
docker-compose up -d

# Recreate your sync schedules
```

## Getting More Help

### Enable Debug Logging

For more detailed logs:

```yaml
# In docker-compose.yml, add environment variable
services:
  app:
    environment:
      - PORT=8000
      - HOST=0.0.0.0
      - LOG_LEVEL=DEBUG  # Add this line
```

### Collect Diagnostic Information

When reporting issues, include:

```bash
# System info
docker --version
docker-compose --version
uname -a  # or systeminfo on Windows

# Container status
docker-compose ps

# Recent logs
docker-compose logs --tail=100 app

# Config (remove sensitive data)
cat docker-compose.yml
```

### Report Issues

If you can't resolve the issue:

1. Check [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues) for similar problems
2. Review the [FAQ](/faq)
3. Open a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Log output
   - System information

## Common Error Messages

### "API not enabled"

**Fix**: Enable Admin SDK API in Google Cloud Console

### "Invalid grant"

**Fix**: Delete token.json and re-authenticate

### "Permission denied"

**Fix**: Authenticate as administrator with proper permissions

### "Resource not found"

**Fix**: Verify OU path or group email is correct

### "Rate limit exceeded"

**Normal**: Operations automatically throttled and retried

## Prevention Best Practices

1. **Always backup** before major operations
2. **Test on small OUs** before large-scale changes
3. **Monitor logs** regularly for warnings
4. **Keep Docker updated** for security patches
5. **Document your syncs** to remember configurations
6. **Use Smart Sync** unless you specifically need Full Sync

Still having issues? Open an issue on [GitHub](https://github.com/rafaelctz/GWorkspace-toolbox/issues) with full details.
