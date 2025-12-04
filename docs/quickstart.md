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

The OU Group Sync feature automatically adds users from an Organizational Unit to a Google Group.

### Steps

1. Click on **OU Group Sync** in the sidebar
2. Enter the **Organizational Unit** path (e.g., `/Students/Grade-10`)
3. Enter the **Target Group Email** (e.g., `grade10-students@school.edu`)
4. Choose sync mode:
   - **Smart Sync**: Only adds new members (preserves manually added teachers/coaches)
   - **Full Sync**: Mirrors OU exactly (removes users not in OU - use for pure class lists)
5. Optionally enable **Schedule Sync** for automatic daily synchronization
6. Click **Sync Now** to run immediately

### Smart Sync vs Full Sync

**Smart Sync** (Recommended):
- Adds users from OU to group
- Never removes anyone from group
- Safe for groups with manually managed members
- Best for most use cases

**Full Sync**:
- Group membership exactly matches OU
- Removes users not in the OU
- Use only if group should mirror OU exactly
- Careful: will remove manually added members

### Scheduling

Enable **Schedule Sync** to automatically run the synchronization daily at midnight. The schedule persists across application restarts.

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
- Use Smart Sync mode unless you specifically need Full Sync
- Export and review CSV files before making bulk changes

### Monitoring
- Check Docker logs for any errors: `docker-compose logs -f`
- Monitor sync job status in the OU Group Sync interface
- Review scheduled sync history regularly

## Next Steps

- Explore detailed [Feature Documentation](/features)
- Review [FAQ](/faq) for common questions
- Check [Troubleshooting](/troubleshooting) if you encounter issues

## Getting Help

Need assistance?
- Check the [FAQ](/faq)
- Visit [GitHub Issues](https://github.com/rafaelctz/GWorkspace-toolbox/issues)
- Review the [Troubleshooting Guide](/troubleshooting)
