# Quick Start Guide

This guide will walk you through using GWorkspace Toolbox features for the first time.

## Prerequisites

- GWorkspace Toolbox installed and running
- Authenticated with your Google Workspace admin account

## Extracting User Aliases

The Alias Extractor allows you to export all user aliases from your domain to a CSV file.

### Steps

1. Open GWorkspace Toolbox at `http://localhost:8000`
2. Click on **Alias Extractor** in the sidebar
3. Ensure you're authenticated (green indicator in top right)
4. Click **Extract Aliases** button
5. Wait for the extraction to complete
6. Download the generated CSV file

### What You Get

The CSV file contains:
- User primary email
- Alias email address
- One row per alias

### Use Cases for Schools

- Audit all student and staff email aliases
- Integrate with Student Information Systems
- Document email routing for directory publishing
- Prepare for email migrations

## Injecting Custom Attributes

The Attribute Injector lets you batch add custom attributes to users in specific Organizational Units.

### Steps

1. Click on **Attribute Injector** in the sidebar
2. Enter or select the target **Organizational Unit** path (e.g., `/Students/Grade-10`)
3. Enter the **Attribute Name** (custom schema field like `SchoolInfo.role`)
4. Enter the **Attribute Value** to assign (e.g., `student`, `teacher`, `staff`)
5. Click **Inject Attributes** button
6. Review the results showing how many users were updated

### Use Cases for Schools

- Assign role types: "student", "teacher", "staff", "admin"
- Set grade levels for students
- Tag users by building or campus
- Apply academic department classifications

## Synchronizing OU to Groups

The OU Group Sync feature automatically synchronizes users from Organizational Units to Google Groups with saved configurations.

### Steps

1. Click on **OU Group Sync** in the sidebar
2. Click **+ New Configuration**
3. Select one or more **Organizational Units** from the tree (e.g., `/Students/Grade-10`)
4. Enter the **Target Group Email** (e.g., `grade10-students@school.edu`)
5. Optionally provide a group name and description
6. Click **Sync** to create the configuration and run the first sync

### How Sync Works

**First Sync (Automatic - Safe Mode):**
- Creates the group if it doesn't exist
- Adds all users from selected OUs to the group
- **Never removes existing group members**
- Safe for groups that already have members

**Subsequent Syncs (Automatic - Mirror Mode):**
- When you click "Resync" on a saved configuration
- Adds users who joined the OU
- **Removes users who left the OU**
- Makes the group mirror the OU exactly

⚠️ **Important**: The system automatically uses safe mode for the first sync, then switches to mirror mode for all subsequent syncs. You cannot manually choose the sync mode - it's determined by whether it's the first time syncing that configuration.

### Managing Configurations

After creating a configuration, you can:
- **Resync**: Update the group with current OU members
- **Sync All**: Run all saved configurations at once
- **Export**: Download configurations for backup
- **Import**: Restore configurations from backup
- **Delete**: Remove configurations you no longer need

## Language Selection

GWorkspace Toolbox supports three languages. Change the language using the dropdown in the top right corner:

- English (EN)
- Español (ES)
- Português (PT)

Your language preference is saved automatically.

## Best Practices

### Security
- Always use admin accounts with minimum required privileges
- Review OAuth permissions before granting access
- Keep credentials.json file secure and never commit to version control

### Testing
- Test operations on small OUs first
- Review group membership before running subsequent syncs (they will remove members not in the OU)
- Export and review CSV files before making bulk changes

### Monitoring
- Check Docker logs for any errors: `docker-compose logs -f`
- Monitor sync job status in the OU Group Sync interface
- Review last sync timestamps on saved configurations

## Next Steps

- Explore detailed [Feature Documentation](/features)
- Review [FAQ](/faq) for common questions
- Check [Troubleshooting](/troubleshooting) if you encounter issues

## Getting Help

Need assistance?
- Check the [FAQ](/faq)
- Visit [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Review the [Troubleshooting Guide](/troubleshooting)
