# OU Group Sync

The OU Group Sync feature automatically synchronizes users from an Organizational Unit to a Google Group, with smart sync capabilities and scheduling options.

![OU Group Sync Interface](/screenshots/ou-group-sync.png)

## Overview

Keeping Google Groups synchronized with Organizational Units can be time-consuming and error-prone when done manually. OU Group Sync automates this process, ensuring groups always reflect their corresponding OUs.

## How It Works

1. **Specify OU**: Enter the organizational unit path (e.g., `/Marketing`)
2. **Select Target Group**: Enter the Google Group email (e.g., `marketing-team@company.com`)
3. **Choose Sync Mode**: Smart Sync or Full Sync
4. **Optional Scheduling**: Enable daily automatic synchronization
5. **Sync**: Click "Sync Now" or let the schedule handle it

## Sync Modes

### Smart Sync (Recommended)

**What it does:**
- Adds all users from the OU to the group
- **Never removes** members from the group
- Preserves manually added members

**Best for:**
- Groups with a mix of OU-based and manually managed members
- Ensuring no one is accidentally removed
- One-way addition of members
- Most common use cases

**Example:**
```
OU Members: alice@, bob@, carol@
Group Before: alice@, dave@ (manually added)
Group After: alice@, bob@, carol@, dave@
```

### Full Sync

**What it does:**
- Makes group membership exactly match the OU
- Adds users from OU
- **Removes users NOT in the OU**

**Best for:**
- Groups that should mirror an OU exactly
- Automated permission groups
- When you want strict OU-to-group mapping

**Example:**
```
OU Members: alice@, bob@, carol@
Group Before: alice@, dave@ (manually added)
Group After: alice@, bob@, carol@
Result: dave@ was removed
```

⚠️ **Warning**: Full Sync will remove manually added members. Only use when you want the group to exactly match the OU.

## Scheduling

### Enable Scheduled Sync

Toggle "Schedule Sync" to enable automatic daily synchronization:

- Runs daily at midnight (server local time)
- Uses the sync mode you specified
- Persists across application restarts
- Stored in SQLite database

### Viewing Scheduled Jobs

The interface shows:
- Currently scheduled sync jobs
- OU and Group being synced
- Sync mode (Smart/Full)
- Schedule status (Active/Inactive)
- Last sync time and result

### Managing Schedules

- **Create**: Enable "Schedule Sync" when configuring a sync
- **Remove**: Click the "Delete" button next to a scheduled job
- **Modify**: Delete the existing schedule and create a new one

## Common Use Cases

### Department Access Groups

Automatically grant department access to resources:

```
OU: /Sales
Group: sales-department@company.com
Mode: Smart Sync
Schedule: Enabled

Result: All sales team members automatically get access to:
- Shared drives
- Internal sites
- Department resources
```

### Team Mailing Lists

Maintain team mailing lists automatically:

```
OU: /Engineering/Backend
Group: backend-team@company.com
Mode: Full Sync
Schedule: Enabled

Result: Group always reflects current backend team roster
```

### Project Groups

Keep project groups up-to-date:

```
OU: /Projects/Phoenix
Group: project-phoenix@company.com
Mode: Smart Sync
Schedule: Enabled

Result: All project members included, plus any external stakeholders
```

### Onboarding Automation

Automatically add new hires to appropriate groups:

```
OU: /New Hires/2024
Group: orientation-2024@company.com
Mode: Smart Sync
Schedule: Enabled

Result: New employees added to group as they're placed in OU
```

### Regional Distribution

Sync regional teams for location-specific communication:

```
OU: /Europe/Germany
Group: germany-team@company.com
Mode: Full Sync
Schedule: Enabled

Result: Only German office members in group
```

## Permissions Required

OU Group Sync requires:

- `https://www.googleapis.com/auth/admin.directory.user.readonly` (read users)
- `https://www.googleapis.com/auth/admin.directory.group` (manage groups)

These permissions allow:
- Reading users from specified OUs
- Adding/removing group members
- Listing existing group membership

## Best Practices

### Choose the Right Sync Mode

| Scenario | Recommended Mode |
|----------|------------------|
| Group has only OU members | Full Sync |
| Group has external members too | Smart Sync |
| Strict access control needed | Full Sync |
| Adding OU members to existing group | Smart Sync |
| Unsure which to use | Smart Sync (safer) |

### Group Naming Conventions

Use clear naming to indicate sync status:
- `team-marketing-auto@company.com` (automatically synced)
- `team-marketing-manual@company.com` (manually managed)

### Documentation

Document your sync configurations:
- Which OUs sync to which groups
- Sync mode used for each
- Purpose of each synced group
- Expected membership counts

### Testing

Before enabling Full Sync:
1. Check current group membership
2. Identify any manually added members
3. Decide if they should remain
4. Consider Smart Sync if unsure

### Monitoring

Regularly review:
- Scheduled sync job status
- Last sync timestamps
- Group membership counts
- Any sync errors in logs

## Group Requirements

### Group Must Exist

The target group must exist before syncing:
1. Create the group in Admin Console or Gmail
2. Note the group email address
3. Use exact email in OU Group Sync

### Group Email Format

Must be a valid Google Group email:
- `team-name@company.com` ✓
- `team.name@company.com` ✓
- `teamname@company.com` ✓
- `invalid-email` ✗

### Group Type

Works with:
- Regular Google Groups
- Security groups
- Mailing lists
- Discussion groups

## Limitations

### OU Depth

The sync operates on the specified OU only. It does NOT include:
- Sub-OUs (nested organizational units)
- Parent OUs

**Example:**
```
/Sales              ← Syncs only direct members
├── /North America  ← NOT included
├── /Europe         ← NOT included
└── /Asia           ← NOT included
```

**Workaround**: Create separate sync jobs for each OU level.

### Group Ownership

The authenticated user must have permission to modify the target group:
- Group owner
- Domain administrator
- Delegated admin with group management rights

### External Members

Smart Sync preserves external members (outside your domain).
Full Sync removes them.

### Nested Groups

The sync adds users directly to groups, not nested groups.

## Performance

- **Small OUs** (< 50 users): 5-15 seconds
- **Medium OUs** (50-500 users): 15-60 seconds
- **Large OUs** (500+ users): 1-5 minutes

Factors affecting speed:
- Number of users in OU
- Current group size
- API response times
- Sync mode (Full Sync is slower)

## Troubleshooting

### "Group not found" Error

The specified group doesn't exist or you lack access.

**Solution:**
1. Verify group email address is correct
2. Check group exists in Admin Console
3. Ensure you have permission to manage the group
4. Try accessing the group in Gmail to confirm

### "OU not found" Error

The organizational unit path is incorrect.

**Solution:**
1. Verify OU path starts with `/`
2. Check exact OU path in Admin Console
3. Path is case-sensitive
4. Ensure no trailing spaces

### No Members Added

Common causes:
- OU is empty
- All users are already in the group
- Permission issues

**Solution:**
1. Check OU has users in Admin Console
2. Verify sync mode is appropriate
3. Check application logs for errors

### Members Unexpectedly Removed

You're using Full Sync mode, which removes users not in the OU.

**Solution:**
1. Switch to Smart Sync if you want to preserve manual members
2. Or add those users to the OU
3. Or re-add them manually after sync

### Schedule Not Running

**Solution:**
1. Check schedule is enabled (toggle should be on)
2. Verify Docker container is running continuously
3. Check logs: `docker-compose logs -f`
4. Ensure database volume is persisted

## API Rate Limits

Google Workspace API limits:
- The tool automatically handles rate limiting
- Large OUs may experience throttling
- Failed operations are retried automatically

## Security Considerations

### Audit Logging

All group membership changes are logged:
- View in Admin Console > Reporting > Audit
- Filter by "Group Settings" events
- Track additions/removals

### Automated Changes

Since changes are automated:
- Document all scheduled syncs
- Monitor group membership regularly
- Review logs for unexpected changes
- Have a rollback plan

### Access Control

- Limit who can configure syncs
- Use dedicated service account if possible
- Monitor scheduled job modifications
- Regular access reviews

## Technical Details

### Implementation

- Uses Google Admin SDK Directory API
- SQLite database for schedule persistence
- APScheduler for cron-like scheduling
- Background job processing

### Scheduling Engine

- Runs at midnight server time (00:00)
- Continues running even if application restarts
- Handles missed jobs if server was down
- Logs all sync operations

### Database Schema

Schedules stored in SQLite:
- OU path
- Group email
- Sync mode (smart/full)
- Schedule status
- Created timestamp
- Last run timestamp

## Advanced Usage

### Multiple Syncs to Same Group

You can sync multiple OUs to one group:

```
Sync 1: /Sales/North America → sales-all@company.com (Smart)
Sync 2: /Sales/Europe → sales-all@company.com (Smart)
Sync 3: /Sales/Asia → sales-all@company.com (Smart)

Result: sales-all@ contains all three regional teams
```

### Sync Chains

Combine with Google Groups nesting:

```
/Marketing → marketing-team@company.com
/Marketing/Content → content-team@company.com

Then: Nest content-team@ inside marketing-team@ in Admin Console
```

### Exclude Specific Users

To exclude certain users from sync:
1. Move them to a different OU
2. Or use Smart Sync and manually remove them (they won't be re-added)

## Next Steps

- Review [Alias Extractor](/features/alias-extractor)
- Learn about [Attribute Injector](/features/attribute-injector)
- Check the [FAQ](/faq) for common questions
