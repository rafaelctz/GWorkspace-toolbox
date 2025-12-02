# DEA Toolbox - Group Sync Enhancement Implementation Plan

**Date:** December 2, 2025
**Project:** DEA Toolbox - Complete Group Sync Overhaul
**Status:** Planning Complete - Ready for Implementation

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Current State](#current-state)
3. [Goals & Requirements](#goals--requirements)
4. [Architecture Changes](#architecture-changes)
5. [Phase 1: Critical Bug Fixes](#phase-1-critical-bug-fixes)
6. [Phase 2: UI/UX Improvements](#phase-2-uiux-improvements)
7. [Phase 3: Smart Sync Engine](#phase-3-smart-sync-engine)
8. [Phase 4: Import/Export](#phase-4-importexport)
9. [Phase 5: Full Sync All](#phase-5-full-sync-all)
10. [Phase 6: Translations](#phase-6-translations)
11. [Implementation Order](#implementation-order)
12. [Testing Checklist](#testing-checklist)
13. [Code Examples](#code-examples)

---

## Project Overview

DEA Toolbox is a Google Workspace administration tool that provides:
- Alias Extractor: Export user email aliases
- Attribute Injector: Bulk update user attributes
- **Group Sync (Focus of this plan)**: Sync Google Groups with Organizational Units

### Current Architecture
- **Backend:** FastAPI + SQLAlchemy + Google Admin SDK
- **Frontend:** React + Vite + i18n (EN/ES/PT)
- **Database:** SQLite with models: GroupSyncConfig, BatchJob, CachedUser
- **Running:** Backend on port 8000, Frontend on port 3000

---

## Current State

### What Works
✅ Basic group sync functionality
✅ Save group configurations
✅ Re-sync button for individual groups
✅ Job queue with progress tracking
✅ Multi-language support (EN, ES, PT)
✅ OAuth and Service Account authentication

### What's Broken
❌ User Status Breakdown not displaying
❌ Failed Users button not working
❌ SSL errors during sync operations
❌ No delta sync (always full sync)
❌ No import/export for configurations
❌ UI is cluttered and not intuitive

---

## Goals & Requirements

### Primary Goals
1. **Fix Critical Bugs:** User status display, failed users list, SSL errors
2. **Smart Sync Engine:** Delta comparison (only sync changes)
3. **Improved UI/UX:** Collapsible sidebar, better layout, modern icons
4. **Import/Export:** Portable configuration files (JSON)
5. **Full Sync All:** Batch process all groups sequentially

### Sync Logic Requirements
- **First-Time Sync:** FULL SYNC (add all members, no removal)
- **Subsequent Syncs:** SMART SYNC (compare current vs expected, add/remove delta)
- **Full Sync All:** Process all saved configs sequentially using SMART SYNC
- **Import Sync:** Determine sync type based on group existence

### User Experience Requirements
- Collapsible sidebar with icons
- Groups displayed as cards in list view
- Create/edit via modal popup
- Compact job queue in side panel
- Export/import buttons in toolbar
- Individual sync + full sync all buttons

---

## Architecture Changes

### Database Schema Updates

**GroupSyncConfig (Add fields):**
```python
is_first_sync = Column(Boolean, default=True)
last_sync_stats = Column(Text, nullable=True)  # JSON
total_syncs = Column(Integer, default=0)
imported_from_file = Column(Boolean, default=False)
import_date = Column(DateTime, nullable=True)
```

### New Components
1. `frontend/src/components/GroupCard.jsx` - Individual group display
2. `frontend/src/components/GroupSyncModal.jsx` - Create/edit modal
3. `frontend/src/components/CompactJobQueue.jsx` - Side panel jobs
4. `frontend/src/components/ImportModal.jsx` - Import configuration
5. `backend/services/smart_sync_engine.py` - Delta sync logic

### Modified Components
- `frontend/src/components/Sidebar.jsx` - Add collapse functionality
- `frontend/src/components/OUGroupSync.jsx` - Major layout refactor
- `frontend/src/components/JobQueue.jsx` - Fix user status display
- `backend/services/group_sync_processor.py` - Add smart sync methods

---

## Phase 1: Critical Bug Fixes

### Priority: HIGHEST | Time: 7 hours

### 1.1 Fix User Status Breakdown Display (2 hours)

**Issue:** User status counts (pending, processing, success, failed) not showing in job details

**Files to modify:**
- `frontend/src/components/JobQueue.jsx`

**Investigation Steps:**
1. Check API response in browser DevTools
2. Verify backend returns `user_status_counts` object
3. Check frontend property access path

**Expected Fix:**
```jsx
// Current (broken):
{job.userStatusCounts?.total}

// Fixed:
{job.user_status_counts?.total || 0}

// Add null checks throughout:
const statusCounts = job.user_status_counts || {
  total: 0,
  pending: 0,
  processing: 0,
  success: 0,
  failed: 0
}
```

**Testing:**
- [ ] Status breakdown shows correct numbers
- [ ] Handles missing data gracefully
- [ ] Updates in real-time during job execution

---

### 1.2 Fix Failed Users Button (3 hours)

**Issue:** Button to view failed users doesn't work

**Files to modify:**
- `frontend/src/components/JobQueue.jsx`
- `backend/main.py` (add new endpoint)
- `backend/services/batch_processor.py`

**Backend Endpoint:**
```python
@router.get("/api/batch/jobs/{job_uuid}/failed-users")
async def get_failed_users(job_uuid: str, db: Session = Depends(get_db)):
    """Get list of users that failed during job processing"""

    # Get failed cached users
    failed_users = db.query(CachedUser).filter(
        CachedUser.job_uuid == job_uuid,
        CachedUser.status == 'failed'
    ).all()

    return {
        "job_uuid": job_uuid,
        "failed_count": len(failed_users),
        "failed_users": [
            {
                "email": user.email,
                "error": user.error_message,
                "timestamp": user.updated_at.isoformat()
            }
            for user in failed_users
        ]
    }
```

**Frontend Implementation:**
```jsx
const [showFailedUsers, setShowFailedUsers] = useState(false)
const [failedUsers, setFailedUsers] = useState([])

const handleViewFailedUsers = async (jobUuid) => {
  const response = await axios.get(
    `${apiBaseUrl}/api/batch/jobs/${jobUuid}/failed-users`
  )
  setFailedUsers(response.data.failed_users)
  setShowFailedUsers(true)
}

// Modal to display failed users
<Modal show={showFailedUsers} onClose={() => setShowFailedUsers(false)}>
  <h3>Failed Users</h3>
  <table>
    <thead>
      <tr>
        <th>Email</th>
        <th>Error</th>
        <th>Time</th>
      </tr>
    </thead>
    <tbody>
      {failedUsers.map(user => (
        <tr key={user.email}>
          <td>{user.email}</td>
          <td>{user.error}</td>
          <td>{new Date(user.timestamp).toLocaleString()}</td>
        </tr>
      ))}
    </tbody>
  </table>
</Modal>
```

**Testing:**
- [ ] Button shows modal with failed users
- [ ] Table displays all failed users with errors
- [ ] Modal closes properly
- [ ] No errors if no failed users

---

### 1.3 SSL Error Fix (2 hours)

**Issue:** SSL errors occur during Google API calls

**Files to modify:**
- `backend/services/google_workspace.py`

**Investigation:**
1. Check backend logs for exact SSL error message:
   ```bash
   tail -f backend/backend.log | grep -i ssl
   ```

2. Common SSL issues:
   - Certificate verification failure
   - TLS version mismatch
   - Timeout treated as SSL error
   - Missing certificate bundle

**Potential Solutions:**

**Option 1: Use certifi for certificate bundle**
```python
import ssl
import certifi
from googleapiclient.discovery import build

# Create SSL context with proper certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Apply to Google API client
service = build(
    'admin',
    'directory_v1',
    credentials=creds,
    # Add SSL context if needed
)
```

**Option 2: Add retry logic with exponential backoff**
```python
from google.api_core import retry
import ssl

@retry.Retry(
    predicate=retry.if_exception_type(ssl.SSLError),
    initial=1.0,
    maximum=10.0,
    multiplier=2.0,
    deadline=60.0
)
def api_call_with_retry(func, *args, **kwargs):
    """Retry API calls that fail with SSL errors"""
    return func(*args, **kwargs)
```

**Option 3: Increase timeout**
```python
service = build(
    'admin',
    'directory_v1',
    credentials=creds,
    timeout=30  # Increase from default 10s
)
```

**Testing:**
- [ ] No SSL errors in logs during sync
- [ ] Syncs complete successfully
- [ ] API calls succeed consistently
- [ ] Performance acceptable with retries

---

## Phase 2: UI/UX Improvements

### Priority: HIGH | Time: 16 hours

### 2.1 Collapsible Sidebar (3 hours)

**Files to modify:**
- `frontend/src/components/Sidebar.jsx`
- Create: `frontend/src/components/Sidebar.css`
- `frontend/src/App.css`

**Implementation:**

```jsx
// Sidebar.jsx
import { useState, useEffect } from 'react'
import './Sidebar.css'

function Sidebar({ currentTool, onToolChange }) {
  const [collapsed, setCollapsed] = useState(
    localStorage.getItem('sidebarCollapsed') === 'true'
  )

  const toggleSidebar = () => {
    const newState = !collapsed
    setCollapsed(newState)
    localStorage.setItem('sidebarCollapsed', newState)
  }

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <button
        className="sidebar-toggle"
        onClick={toggleSidebar}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? '→' : '←'}
      </button>

      <div className="sidebar-header">
        {!collapsed && <h2>{t('tools.title')}</h2>}
      </div>

      <nav className="sidebar-nav">
        {tools.map(tool => (
          <button
            key={tool.id}
            className={`tool-item ${currentTool === tool.id ? 'active' : ''}`}
            onClick={() => onToolChange(tool.id)}
            data-tooltip={collapsed ? tool.name : ''}
          >
            <span className="tool-icon">{tool.icon}</span>
            {!collapsed && (
              <div className="tool-info">
                <span className="tool-name">{tool.name}</span>
                <span className="tool-description">{tool.description}</span>
              </div>
            )}
          </button>
        ))}
      </nav>
    </div>
  )
}
```

**CSS:**
```css
/* Sidebar.css */
.sidebar {
  width: 250px;
  height: 100vh;
  background: #f5f5f5;
  border-right: 1px solid #ddd;
  transition: width 0.3s ease;
  position: relative;
  overflow-x: hidden;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-toggle {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  border: none;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  z-index: 10;
}

.sidebar.collapsed .tool-name,
.sidebar.collapsed .tool-description,
.sidebar.collapsed .sidebar-header h2 {
  display: none;
}

.tool-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: none;
  background: transparent;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}

.tool-item:hover {
  background: #e0e0e0;
}

.tool-item.active {
  background: #2196F3;
  color: white;
}

/* Tooltip for collapsed state */
.sidebar.collapsed .tool-item {
  position: relative;
  justify-content: center;
}

.sidebar.collapsed .tool-item:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background: #333;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 100;
  margin-left: 8px;
  font-size: 14px;
}
```

**Testing:**
- [ ] Sidebar collapses/expands smoothly
- [ ] State persists across page reloads
- [ ] Tooltips show in collapsed mode
- [ ] No layout issues when toggling
- [ ] Mobile responsive (if applicable)

---

### 2.2 Better Icons (1 hour)

**Files to modify:**
- `frontend/src/components/Sidebar.jsx`
- `package.json`

**Installation:**
```bash
cd frontend
npm install react-icons
```

**Implementation:**
```jsx
import {
  HiOutlineMail,           // Alias Extractor
  HiOutlineDatabase,       // Attribute Injector
  HiOutlineUserGroup       // Group Sync
} from 'react-icons/hi2'

const tools = [
  {
    id: 'alias-extractor',
    name: t('tools.aliasExtractor.title'),
    icon: <HiOutlineMail size={24} />,
    description: t('tools.aliasExtractor.description')
  },
  {
    id: 'attribute-injector',
    name: t('tools.attributeInjector.title'),
    icon: <HiOutlineDatabase size={24} />,
    description: t('tools.attributeInjector.description')
  },
  {
    id: 'group-sync',
    name: t('tools.groupSync.title'),
    icon: <HiOutlineUserGroup size={24} />,
    description: t('tools.groupSync.description')
  }
]
```

**Alternative Icon Libraries:**
- `react-icons` (recommended - includes many icon sets)
- `@heroicons/react` (Tailwind's icon set)
- Custom SVG icons

**Testing:**
- [ ] Icons display correctly
- [ ] Icons scale properly in collapsed mode
- [ ] Icons are intuitive for each tool
- [ ] Accessible with screen readers

---

### 2.3 Redesign Group Sync Layout (12 hours)

This is the major UI overhaul. See detailed implementation in [Code Examples](#code-examples) section.

**New Layout Structure:**
```
┌─────────────────────────────────────────────────────────┐
│ OU to Group Sync                                        │
│ [📥 Export] [📤 Import] [🔄 Full Sync All] [➕ New]    │
├─────────────────────────────────────────────────────────┤
│ Saved Groups                               Active Jobs  │
│ ┌────────────────────────────┐  ┌──────────────────┐  │
│ │ 📧 alunos@domain.com [Sync]│  │ Job #123         │  │
│ │ 4 OUs • 256 members        │  │ ████████░░ 78%   │  │
│ │ Last: 2h ago  +12 -3 =241  │  │                  │  │
│ │ [Edit] [Delete]            │  │ Job #124         │  │
│ └────────────────────────────┘  │ ██████████ 100%  │  │
│                                  │                  │  │
│ ┌────────────────────────────┐  │ [View All]       │  │
│ │ 📧 prof@domain.com   [Sync]│  └──────────────────┘  │
│ │ 1 OU • 45 members          │                        │
│ │ Last: 1d ago  No changes   │                        │
│ │ [Edit] [Delete]            │                        │
│ └────────────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

**Components to create:**

1. **GroupCard.jsx** (see Code Examples)
2. **GroupSyncModal.jsx** (see Code Examples)
3. **CompactJobQueue.jsx** (see Code Examples)
4. **ImportModal.jsx** (see Code Examples)

**Files to modify:**
- Refactor `OUGroupSync.jsx` completely
- Update `AttributeInjector.css` or create `GroupSync.css`

---

## Phase 3: Smart Sync Engine

### Priority: HIGHEST | Time: 10 hours

### 3.1 Database Schema Updates (1 hour)

**Create migration script:**
```bash
touch backend/migrations/add_smart_sync_fields.py
```

**Migration Script:**
```python
"""Add smart sync tracking fields to GroupSyncConfig"""
from sqlalchemy import text
from database.session import engine

def upgrade():
    """Add new fields for smart sync tracking"""
    with engine.connect() as conn:
        # Track if this is first sync
        conn.execute(text("""
            ALTER TABLE group_sync_configs
            ADD COLUMN is_first_sync BOOLEAN DEFAULT TRUE
        """))

        # Store last sync statistics
        conn.execute(text("""
            ALTER TABLE group_sync_configs
            ADD COLUMN last_sync_stats TEXT NULL
        """))

        # Count total syncs
        conn.execute(text("""
            ALTER TABLE group_sync_configs
            ADD COLUMN total_syncs INTEGER DEFAULT 0
        """))

        # Track imports
        conn.execute(text("""
            ALTER TABLE group_sync_configs
            ADD COLUMN imported_from_file BOOLEAN DEFAULT FALSE
        """))

        conn.execute(text("""
            ALTER TABLE group_sync_configs
            ADD COLUMN import_date DATETIME NULL
        """))

        conn.commit()
        print("✅ Migration completed successfully")

def downgrade():
    """Remove added fields"""
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE group_sync_configs
            DROP COLUMN is_first_sync
        """))
        conn.execute(text("""
            ALTER TABLE group_sync_configs
            DROP COLUMN last_sync_stats
        """))
        conn.execute(text("""
            ALTER TABLE group_sync_configs
            DROP COLUMN total_syncs
        """))
        conn.execute(text("""
            ALTER TABLE group_sync_configs
            DROP COLUMN imported_from_file
        """))
        conn.execute(text("""
            ALTER TABLE group_sync_configs
            DROP COLUMN import_date
        """))
        conn.commit()

if __name__ == "__main__":
    upgrade()
```

**Run migration:**
```bash
cd backend
python migrations/add_smart_sync_fields.py
```

**Update models.py:**
```python
class GroupSyncConfig(Base):
    """Saved configurations for OU to Group syncing"""
    __tablename__ = 'group_sync_configs'

    # ... existing fields ...

    # Smart sync tracking
    is_first_sync = Column(Boolean, default=True)
    last_sync_stats = Column(Text, nullable=True)  # JSON
    total_syncs = Column(Integer, default=0)

    # Import/export tracking
    imported_from_file = Column(Boolean, default=False)
    import_date = Column(DateTime, nullable=True)
```

---

### 3.2 Smart Sync Implementation (6 hours)

**Files to modify:**
- `backend/services/group_sync_processor.py`
- `backend/services/google_workspace.py` (add get_group_members if missing)

**Core Logic:**

```python
def smart_sync(self, config_uuid: str) -> Dict:
    """
    Performs delta-based synchronization
    Compares current group members with expected members from OUs
    Only adds/removes members that changed

    Returns:
        Dict with sync statistics: added, removed, unchanged, failed
    """
    print(f"[SmartSync] Starting for config {config_uuid}")

    config = self.db.query(GroupSyncConfig).filter(
        GroupSyncConfig.config_uuid == config_uuid
    ).first()

    if not config:
        raise Exception(f"Config {config_uuid} not found")

    # STEP 1: Get CURRENT members from Google Group
    print(f"[SmartSync] Fetching current members from {config.group_email}")
    try:
        current_members = self.google_service.list_group_members(
            config.group_email
        )
        current_emails = {m['email'].lower() for m in current_members}
        print(f"[SmartSync] Current group has {len(current_emails)} members")
    except Exception as e:
        print(f"[SmartSync] Error fetching group members: {e}")
        # If group doesn't exist or error, assume empty
        current_emails = set()

    # STEP 2: Get EXPECTED members from OUs
    print(f"[SmartSync] Fetching expected members from OUs")
    ou_paths = json.loads(config.ou_paths)
    expected_members = []

    for ou_path in ou_paths:
        print(f"[SmartSync] Getting users from {ou_path}")
        users = self.google_service.get_users_in_ou(ou_path)
        expected_members.extend(users)
        print(f"[SmartSync] Found {len(users)} users in {ou_path}")

    # Remove duplicates (users in multiple OUs)
    expected_emails = {u['email'].lower() for u in expected_members}
    print(f"[SmartSync] Expected {len(expected_emails)} unique members")

    # STEP 3: Calculate DELTA
    to_add = expected_emails - current_emails
    to_remove = current_emails - expected_emails
    unchanged = current_emails & expected_emails

    print(f"[SmartSync] Delta calculation:")
    print(f"  To Add: {len(to_add)}")
    print(f"  To Remove: {len(to_remove)}")
    print(f"  Unchanged: {len(unchanged)}")

    # STEP 4: Apply changes with rate limiting
    stats = {
        'added': 0,
        'removed': 0,
        'unchanged': len(unchanged),
        'failed_add': 0,
        'failed_remove': 0,
        'errors': []
    }

    # Add missing members
    for email in to_add:
        try:
            print(f"[SmartSync] Adding member: {email}")
            self.google_service.add_group_member(
                config.group_email,
                email
            )
            stats['added'] += 1
            time.sleep(self.API_CALL_DELAY)  # Rate limiting
        except Exception as e:
            print(f"[SmartSync] Failed to add {email}: {str(e)}")
            stats['failed_add'] += 1
            stats['errors'].append({
                'email': email,
                'action': 'add',
                'error': str(e)
            })

    # Remove extra members
    for email in to_remove:
        try:
            print(f"[SmartSync] Removing member: {email}")
            self.google_service.remove_group_member(
                config.group_email,
                email
            )
            stats['removed'] += 1
            time.sleep(self.API_CALL_DELAY)
        except Exception as e:
            print(f"[SmartSync] Failed to remove {email}: {str(e)}")
            stats['failed_remove'] += 1
            stats['errors'].append({
                'email': email,
                'action': 'remove',
                'error': str(e)
            })

    # STEP 5: Update config with stats
    config.last_sync_stats = json.dumps(stats)
    config.last_synced_at = datetime.utcnow()
    config.total_syncs += 1
    config.is_first_sync = False
    self.db.commit()

    print(f"[SmartSync] Completed: +{stats['added']} -{stats['removed']} ={stats['unchanged']}")
    return stats


def full_sync(self, config_uuid: str) -> Dict:
    """
    First-time sync: Only ADDS members, no removal
    Used when group is first created or imported

    Returns:
        Dict with sync statistics
    """
    print(f"[FullSync] Starting for config {config_uuid}")

    config = self.db.query(GroupSyncConfig).filter(
        GroupSyncConfig.config_uuid == config_uuid
    ).first()

    if not config:
        raise Exception(f"Config {config_uuid} not found")

    # Get all users from OUs
    ou_paths = json.loads(config.ou_paths)
    all_users = []

    for ou_path in ou_paths:
        print(f"[FullSync] Getting users from {ou_path}")
        users = self.google_service.get_users_in_ou(ou_path)
        all_users.extend(users)

    # Remove duplicates
    unique_users = {u['email']: u for u in all_users}.values()
    print(f"[FullSync] Total unique users to add: {len(unique_users)}")

    # Add all to group (skip already members)
    stats = {
        'added': 0,
        'failed_add': 0,
        'errors': []
    }

    for user in unique_users:
        try:
            self.google_service.add_group_member(
                config.group_email,
                user['email']
            )
            stats['added'] += 1
            time.sleep(self.API_CALL_DELAY)
        except Exception as e:
            # Check if already a member (not an error)
            if 'already a member' in str(e).lower() or 'duplicate' in str(e).lower():
                stats['added'] += 1
                print(f"[FullSync] {user['email']} already in group")
            else:
                stats['failed_add'] += 1
                stats['errors'].append({
                    'email': user['email'],
                    'error': str(e)
                })
                print(f"[FullSync] Failed to add {user['email']}: {str(e)}")

    # Update config
    config.last_sync_stats = json.dumps(stats)
    config.last_synced_at = datetime.utcnow()
    config.total_syncs += 1
    config.is_first_sync = False
    self.db.commit()

    print(f"[FullSync] Completed: {stats['added']} members added")
    return stats


def process_sync(self, config_uuid: str, force_full: bool = False) -> Dict:
    """
    Determines sync type and executes

    Args:
        config_uuid: Configuration to sync
        force_full: Force full sync even if not first time

    Returns:
        Dict with sync results
    """
    config = self.db.query(GroupSyncConfig).filter(
        GroupSyncConfig.config_uuid == config_uuid
    ).first()

    if not config:
        raise Exception(f"Config {config_uuid} not found")

    # Determine sync type
    if force_full or config.is_first_sync:
        print(f"[Sync] Performing FULL SYNC for {config.group_email}")
        return self.full_sync(config_uuid)
    else:
        print(f"[Sync] Performing SMART SYNC for {config.group_email}")
        return self.smart_sync(config_uuid)
```

**Add missing method to google_workspace.py:**

```python
def list_group_members(self, group_email: str) -> List[Dict]:
    """
    Get all members of a Google Group

    Args:
        group_email: Email of the group

    Returns:
        List of member dictionaries with email, role, type
    """
    try:
        members = []
        page_token = None

        while True:
            results = self.service.members().list(
                groupKey=group_email,
                pageToken=page_token
            ).execute()

            members.extend(results.get('members', []))

            page_token = results.get('nextPageToken')
            if not page_token:
                break

        return members
    except Exception as e:
        print(f"Error listing group members: {e}")
        raise


def remove_group_member(self, group_email: str, member_email: str):
    """
    Remove a member from a Google Group

    Args:
        group_email: Email of the group
        member_email: Email of the member to remove
    """
    try:
        self.service.members().delete(
            groupKey=group_email,
            memberKey=member_email
        ).execute()
        print(f"Removed {member_email} from {group_email}")
    except Exception as e:
        print(f"Error removing member: {e}")
        raise
```

---

### 3.3 Update API Endpoints (3 hours)

**Files to modify:**
- `backend/main.py`

**Update existing re-sync endpoint:**
```python
@router.post("/api/group-sync/configs/{config_uuid}/sync")
async def sync_group_config(
    config_uuid: str,
    force_full: bool = False,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Trigger sync for a specific configuration

    Args:
        config_uuid: Configuration to sync
        force_full: Force full sync (default: smart sync)
    """
    try:
        google_service = get_google_service(db)
        processor = GroupSyncProcessor(db, google_service)

        # Check if group exists in Google
        config = processor.db.query(GroupSyncConfig).filter(
            GroupSyncConfig.config_uuid == config_uuid
        ).first()

        group_exists = google_service.get_group(config.group_email)

        if not group_exists:
            # Create group first
            google_service.create_group(
                group_email=config.group_email,
                group_name=config.group_name,
                description=config.group_description
            )
            force_full = True  # First sync must be full

        # Process sync
        result = processor.process_sync(config_uuid, force_full=force_full)

        # Update config last sync timestamp
        config.last_synced_at = datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "config_uuid": config_uuid,
            "group_email": config.group_email,
            "sync_type": "full" if force_full or config.is_first_sync else "smart",
            "stats": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Phase 4: Import/Export

### Priority: MEDIUM | Time: 7 hours

### 4.1 Export Functionality (3 hours)

**Files to modify:**
- `backend/main.py`
- `frontend/src/components/OUGroupSync.jsx`

**Backend Endpoint:**
```python
@router.get("/api/group-sync/export")
async def export_configurations(
    format: str = "json",
    db: Session = Depends(get_db)
):
    """
    Export all group sync configurations to JSON

    Args:
        format: Export format (json or xml) - currently only json supported

    Returns:
        JSON file download
    """
    try:
        google_service = get_google_service(db)
        processor = GroupSyncProcessor(db, google_service)

        configs = processor.get_all_configs()

        export_data = {
            "version": "1.0",
            "export_date": datetime.utcnow().isoformat(),
            "domain": get_current_domain(db),
            "total_configurations": len(configs),
            "configurations": []
        }

        for config in configs:
            # Get current member count from Google
            try:
                members = google_service.list_group_members(config['group_email'])
                member_count = len(members)
            except:
                member_count = 0

            export_data["configurations"].append({
                "group_email": config['group_email'],
                "group_name": config['group_name'],
                "group_description": config['group_description'],
                "organizational_units": config['ou_paths'],
                "created_at": config['created_at'],
                "last_synced_at": config['last_synced_at'],
                "total_syncs": config.get('total_syncs', 0),
                "current_member_count": member_count,
                "last_sync_stats": json.loads(config['last_sync_stats']) if config.get('last_sync_stats') else None
            })

        # Return as downloadable file
        from fastapi.responses import JSONResponse

        filename = f"dea_toolbox_groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_current_domain(db: Session) -> str:
    """Get domain from active credential"""
    cred = db.query(Credential).filter(Credential.is_active == True).first()
    return cred.domain if cred else "unknown"
```

**Frontend Implementation:**
```jsx
const handleExportConfigs = async () => {
  try {
    setMessage({ type: '', text: '' })

    const response = await axios.get(
      `${apiBaseUrl}/api/group-sync/export?format=json`,
      {
        responseType: 'blob',
        headers: {
          'Accept': 'application/json'
        }
      }
    )

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url

    // Extract filename from response headers or use default
    const contentDisposition = response.headers['content-disposition']
    let filename = 'group_configs.json'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }

    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    setMessage({
      type: 'success',
      text: t('groupSync.exportSuccess')
    })
  } catch (error) {
    console.error('Export failed:', error)
    setMessage({
      type: 'error',
      text: error.response?.data?.detail || t('groupSync.exportError')
    })
  }
}
```

---

### 4.2 Import Functionality (4 hours)

**Files to modify:**
- `backend/main.py`
- `frontend/src/components/OUGroupSync.jsx`
- Create: `frontend/src/components/ImportModal.jsx`

**Backend Endpoint:**
```python
@router.post("/api/group-sync/import")
async def import_configurations(
    file: UploadFile,
    apply_sync: bool = True,
    db: Session = Depends(get_db)
):
    """
    Import group configurations from JSON file

    Args:
        file: JSON file with configurations
        apply_sync: Whether to sync after import (default: True)

    Returns:
        Import results with sync statistics
    """
    try:
        # Read and parse file
        content = await file.read()
        data = json.loads(content)

        # Validate format
        if 'version' not in data or 'configurations' not in data:
            raise HTTPException(400, "Invalid file format")

        # Validate domain
        current_domain = get_current_domain(db)
        if data.get('domain') and data['domain'] != current_domain:
            raise HTTPException(
                400,
                f"Domain mismatch: File is for {data['domain']}, but you're authenticated with {current_domain}"
            )

        google_service = get_google_service(db)
        processor = GroupSyncProcessor(db, google_service)

        results = []

        for config_data in data['configurations']:
            try:
                # Check if group exists in Google
                group_exists = google_service.get_group(config_data['group_email'])

                # Check if config already exists in database
                existing_config = db.query(GroupSyncConfig).filter(
                    GroupSyncConfig.group_email == config_data['group_email']
                ).first()

                if existing_config:
                    # Update existing
                    existing_config.ou_paths = json.dumps(config_data['organizational_units'])
                    existing_config.group_name = config_data['group_name']
                    existing_config.group_description = config_data.get('group_description')
                    existing_config.updated_at = datetime.utcnow()
                    existing_config.imported_from_file = True
                    existing_config.import_date = datetime.utcnow()
                    db.commit()

                    config_uuid = existing_config.config_uuid
                    action = 'updated'
                else:
                    # Create new config
                    config = processor.create_or_update_config(
                        ou_paths=config_data['organizational_units'],
                        group_email=config_data['group_email'],
                        group_name=config_data['group_name'],
                        group_description=config_data.get('group_description'),
                        domain=current_domain
                    )
                    config.imported_from_file = True
                    config.import_date = datetime.utcnow()
                    db.commit()

                    config_uuid = config.config_uuid
                    action = 'created'

                # Apply sync if requested
                sync_result = None
                if apply_sync:
                    if not group_exists:
                        # Create group + full sync
                        google_service.create_group(
                            group_email=config_data['group_email'],
                            group_name=config_data['group_name'],
                            description=config_data.get('group_description', '')
                        )
                        sync_result = processor.full_sync(config_uuid)
                        sync_type = 'full'
                    else:
                        # Smart sync
                        sync_result = processor.smart_sync(config_uuid)
                        sync_type = 'smart'
                else:
                    sync_type = 'skipped'

                results.append({
                    'group_email': config_data['group_email'],
                    'action': action,
                    'synced': apply_sync,
                    'sync_type': sync_type,
                    'stats': sync_result
                })

            except Exception as e:
                results.append({
                    'group_email': config_data['group_email'],
                    'action': 'failed',
                    'error': str(e)
                })

        return {
            'total_imported': len(data['configurations']),
            'successful': len([r for r in results if r['action'] != 'failed']),
            'failed': len([r for r in results if r['action'] == 'failed']),
            'results': results
        }

    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON file")
    except Exception as e:
        raise HTTPException(500, str(e))
```

**Frontend ImportModal Component:**
```jsx
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import './ImportModal.css'

function ImportModal({ show, onClose, onImport, apiBaseUrl }) {
  const { t } = useTranslation()
  const [file, setFile] = useState(null)
  const [applySync, setApplySync] = useState(true)
  const [importing, setImporting] = useState(false)
  const [preview, setPreview] = useState(null)

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0]
    if (!selectedFile) return

    setFile(selectedFile)

    // Preview file contents
    try {
      const text = await selectedFile.text()
      const data = JSON.parse(text)
      setPreview({
        total: data.configurations?.length || 0,
        domain: data.domain,
        exportDate: data.export_date
      })
    } catch (err) {
      alert(t('groupSync.import.invalidFile'))
    }
  }

  const handleImport = async () => {
    if (!file) return

    setImporting(true)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(
        `${apiBaseUrl}/api/group-sync/import?apply_sync=${applySync}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )

      onImport(response.data)
      onClose()
    } catch (error) {
      alert(error.response?.data?.detail || t('groupSync.import.error'))
    } finally {
      setImporting(false)
    }
  }

  if (!show) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{t('groupSync.import.title')}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="file-input-wrapper">
            <input
              type="file"
              accept=".json"
              onChange={handleFileChange}
              id="import-file"
            />
            <label htmlFor="import-file" className="btn btn-secondary">
              {file ? file.name : t('groupSync.import.selectFile')}
            </label>
          </div>

          {preview && (
            <div className="import-preview">
              <h4>{t('groupSync.import.preview')}</h4>
              <p>{t('groupSync.import.configurationsFound', { count: preview.total })}</p>
              <p>{t('groupSync.import.domain')}: {preview.domain}</p>
              <p>{t('groupSync.import.exportedOn')}: {new Date(preview.exportDate).toLocaleString()}</p>
            </div>
          )}

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={applySync}
              onChange={(e) => setApplySync(e.target.checked)}
            />
            <span>{t('groupSync.import.applySync')}</span>
            <small>{t('groupSync.import.applySyncHelp')}</small>
          </label>
        </div>

        <div className="modal-footer">
          <button
            className="btn btn-secondary"
            onClick={onClose}
            disabled={importing}
          >
            {t('common.cancel')}
          </button>
          <button
            className="btn btn-primary"
            onClick={handleImport}
            disabled={!file || importing}
          >
            {importing ? t('groupSync.import.importing') : t('groupSync.import.confirm')}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ImportModal
```

---

## Phase 5: Full Sync All

### Priority: MEDIUM | Time: 2 hours

**Files to modify:**
- `backend/main.py`
- `frontend/src/components/OUGroupSync.jsx`

**Backend Endpoint:**
```python
@router.post("/api/group-sync/full-sync-all")
async def full_sync_all_groups(
    db: Session = Depends(get_db)
):
    """
    Trigger smart sync for ALL saved group configurations
    Processes sequentially (cascaded) one at a time
    Each sync uses smart sync (delta comparison)

    Returns:
        Results for all synced groups
    """
    try:
        google_service = get_google_service(db)
        processor = GroupSyncProcessor(db, google_service)

        # Get all configs
        configs = processor.get_all_configs()

        if not configs:
            return {
                'total_configs': 0,
                'message': 'No configurations to sync'
            }

        print(f"[FullSyncAll] Starting sync for {len(configs)} groups")

        results = []

        # Process each config sequentially
        for idx, config in enumerate(configs, 1):
            print(f"[FullSyncAll] Processing {idx}/{len(configs)}: {config['group_email']}")

            try:
                # Always use smart sync for "Full Sync All"
                stats = processor.smart_sync(config['config_uuid'])

                results.append({
                    'config_uuid': config['config_uuid'],
                    'group_email': config['group_email'],
                    'status': 'success',
                    'stats': stats
                })

                print(f"[FullSyncAll] ✅ {config['group_email']}: +{stats['added']} -{stats['removed']}")

            except Exception as e:
                print(f"[FullSyncAll] ❌ {config['group_email']}: {str(e)}")
                results.append({
                    'config_uuid': config['config_uuid'],
                    'group_email': config['group_email'],
                    'status': 'failed',
                    'error': str(e)
                })

        successful = len([r for r in results if r['status'] == 'success'])
        failed = len([r for r in results if r['status'] == 'failed'])

        print(f"[FullSyncAll] Completed: {successful} successful, {failed} failed")

        return {
            'total_configs': len(configs),
            'successful': successful,
            'failed': failed,
            'results': results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Frontend Implementation:**
```jsx
const [fullSyncing, setFullSyncing] = useState(false)

const handleFullSyncAll = async () => {
  if (!confirm(t('groupSync.fullSyncAll.confirm'))) {
    return
  }

  setFullSyncing(true)
  setMessage({ type: '', text: '' })

  try {
    const response = await axios.post(
      `${apiBaseUrl}/api/group-sync/full-sync-all`
    )

    setMessage({
      type: 'success',
      text: t('groupSync.fullSyncAll.completed', {
        successful: response.data.successful,
        total: response.data.total_configs
      })
    })

    // Refresh configs to show updated stats
    fetchConfigs()

  } catch (error) {
    setMessage({
      type: 'error',
      text: error.response?.data?.detail || t('groupSync.fullSyncAll.error')
    })
  } finally {
    setFullSyncing(false)
  }
}

// In JSX:
<button
  onClick={handleFullSyncAll}
  className="btn btn-primary"
  disabled={fullSyncing || configs.length === 0}
>
  {fullSyncing ? (
    <>
      <span className="spinner"></span>
      {t('groupSync.fullSyncAll.syncing')}
    </>
  ) : (
    <>
      🔄 {t('groupSync.fullSyncAll.button')}
    </>
  )}
</button>
```

---

## Phase 6: Translations

### Priority: LOW | Time: 2 hours

**Files to modify:**
- `frontend/src/locales/en.json`
- `frontend/src/locales/es.json`
- `frontend/src/locales/pt.json`

**Add to all three language files:**

**English (en.json):**
```json
{
  "sidebar": {
    "collapse": "Collapse sidebar",
    "expand": "Expand sidebar"
  },
  "groupSync": {
    "exportConfigs": "Export All",
    "exportSuccess": "Configurations exported successfully",
    "exportError": "Failed to export configurations",

    "importConfigs": "Import",
    "import": {
      "title": "Import Configurations",
      "selectFile": "Select JSON file",
      "preview": "Preview",
      "configurationsFound": "{count} configurations found",
      "domain": "Domain",
      "exportedOn": "Exported on",
      "applySync": "Apply smart sync after import",
      "applySyncHelp": "Automatically sync group members after importing configuration",
      "importing": "Importing...",
      "confirm": "Import",
      "invalidFile": "Invalid file format",
      "error": "Import failed",
      "success": "Import completed successfully"
    },

    "fullSyncAll": {
      "button": "Full Sync All",
      "confirm": "This will sync all {count} groups. Continue?",
      "syncing": "Syncing all groups...",
      "completed": "Full sync completed: {successful} of {total} groups synced successfully",
      "error": "Full sync failed"
    },

    "createNew": "Create New",
    "editGroup": "Edit Group",
    "noGroups": "No groups configured yet",

    "syncStats": {
      "added": "Added",
      "removed": "Removed",
      "unchanged": "Unchanged",
      "failed": "Failed"
    },

    "syncType": {
      "full": "Full Sync",
      "smart": "Smart Sync",
      "firstTime": "(First Time)"
    }
  }
}
```

**Spanish (es.json):**
```json
{
  "sidebar": {
    "collapse": "Contraer barra lateral",
    "expand": "Expandir barra lateral"
  },
  "groupSync": {
    "exportConfigs": "Exportar Todo",
    "exportSuccess": "Configuraciones exportadas exitosamente",
    "exportError": "Error al exportar configuraciones",

    "importConfigs": "Importar",
    "import": {
      "title": "Importar Configuraciones",
      "selectFile": "Seleccionar archivo JSON",
      "preview": "Vista previa",
      "configurationsFound": "{count} configuraciones encontradas",
      "domain": "Dominio",
      "exportedOn": "Exportado en",
      "applySync": "Aplicar sincronización inteligente después de importar",
      "applySyncHelp": "Sincronizar automáticamente miembros del grupo después de importar la configuración",
      "importing": "Importando...",
      "confirm": "Importar",
      "invalidFile": "Formato de archivo inválido",
      "error": "Importación fallida",
      "success": "Importación completada exitosamente"
    },

    "fullSyncAll": {
      "button": "Sincronizar Todo",
      "confirm": "Esto sincronizará todos los {count} grupos. ¿Continuar?",
      "syncing": "Sincronizando todos los grupos...",
      "completed": "Sincronización completa: {successful} de {total} grupos sincronizados exitosamente",
      "error": "Sincronización completa fallida"
    },

    "createNew": "Crear Nuevo",
    "editGroup": "Editar Grupo",
    "noGroups": "No hay grupos configurados aún",

    "syncStats": {
      "added": "Agregados",
      "removed": "Eliminados",
      "unchanged": "Sin cambios",
      "failed": "Fallidos"
    },

    "syncType": {
      "full": "Sincronización Completa",
      "smart": "Sincronización Inteligente",
      "firstTime": "(Primera Vez)"
    }
  }
}
```

**Portuguese (pt.json):**
```json
{
  "sidebar": {
    "collapse": "Recolher barra lateral",
    "expand": "Expandir barra lateral"
  },
  "groupSync": {
    "exportConfigs": "Exportar Tudo",
    "exportSuccess": "Configurações exportadas com sucesso",
    "exportError": "Falha ao exportar configurações",

    "importConfigs": "Importar",
    "import": {
      "title": "Importar Configurações",
      "selectFile": "Selecionar arquivo JSON",
      "preview": "Visualizar",
      "configurationsFound": "{count} configurações encontradas",
      "domain": "Domínio",
      "exportedOn": "Exportado em",
      "applySync": "Aplicar sincronização inteligente após importar",
      "applySyncHelp": "Sincronizar automaticamente membros do grupo após importar configuração",
      "importing": "Importando...",
      "confirm": "Importar",
      "invalidFile": "Formato de arquivo inválido",
      "error": "Importação falhou",
      "success": "Importação concluída com sucesso"
    },

    "fullSyncAll": {
      "button": "Sincronizar Tudo",
      "confirm": "Isso sincronizará todos os {count} grupos. Continuar?",
      "syncing": "Sincronizando todos os grupos...",
      "completed": "Sincronização completa: {successful} de {total} grupos sincronizados com sucesso",
      "error": "Sincronização completa falhou"
    },

    "createNew": "Criar Novo",
    "editGroup": "Editar Grupo",
    "noGroups": "Nenhum grupo configurado ainda",

    "syncStats": {
      "added": "Adicionados",
      "removed": "Removidos",
      "unchanged": "Inalterados",
      "failed": "Falharam"
    },

    "syncType": {
      "full": "Sincronização Completa",
      "smart": "Sincronização Inteligente",
      "firstTime": "(Primeira Vez)"
    }
  }
}
```

---

## Implementation Order

### Week 1: Critical Fixes (7 hours)
**Goal:** Fix all broken functionality

- [ ] Day 1-2: Fix User Status Breakdown (2h)
- [ ] Day 2-3: Fix Failed Users Button (3h)
- [ ] Day 3: SSL Error Investigation & Fix (2h)
- [ ] Day 3: Test all fixes

### Week 2: Smart Sync Core (10 hours)
**Goal:** Implement delta sync logic

- [ ] Day 1: Database schema updates (1h)
- [ ] Day 1-2: Implement `smart_sync()` function (4h)
- [ ] Day 2: Implement `full_sync()` function (2h)
- [ ] Day 3: Update API endpoints (2h)
- [ ] Day 3: Test sync logic thoroughly (1h)

### Week 3: UI Improvements (16 hours)
**Goal:** Modern, intuitive interface

- [ ] Day 1: Collapsible sidebar (3h)
- [ ] Day 1: Better icons (1h)
- [ ] Day 2: Create GroupCard component (2h)
- [ ] Day 2: Create CompactJobQueue (2h)
- [ ] Day 3-4: Create GroupSyncModal (4h)
- [ ] Day 4-5: Refactor OUGroupSync layout (4h)

### Week 4: Import/Export & Final (9 hours)
**Goal:** Complete all features

- [ ] Day 1: Export functionality (3h)
- [ ] Day 2: Import functionality (4h)
- [ ] Day 3: Full Sync All feature (2h)
- [ ] Day 3: Add translations (2h)
- [ ] Day 4-5: End-to-end testing (4h)

**Total Time Estimate: 42 hours (approx. 5-6 working days)**

---

## Testing Checklist

### Phase 1: Bug Fixes
- [ ] User status breakdown displays correctly for all job types
- [ ] Status counts update in real-time during job execution
- [ ] Failed users button shows modal with complete list
- [ ] Failed users table shows email + error + timestamp
- [ ] SSL errors are resolved (check backend logs)
- [ ] No connection issues during sync operations
- [ ] API calls complete successfully without timeouts

### Phase 2: UI/UX
- [ ] Sidebar collapses/expands smoothly with animation
- [ ] Sidebar state persists across page reloads
- [ ] Tooltips appear when sidebar is collapsed
- [ ] Icons are clear and intuitive for each tool
- [ ] Icons scale properly in collapsed mode
- [ ] Group cards display all information correctly
- [ ] Compact job queue shows recent jobs
- [ ] Modal opens/closes without issues
- [ ] Layout is responsive (test different screen sizes)
- [ ] No visual glitches or overlapping elements

### Phase 3: Smart Sync
- [ ] First sync performs FULL SYNC (adds all, no removal)
- [ ] `is_first_sync` flag is set to False after first sync
- [ ] Subsequent syncs perform SMART SYNC (delta)
- [ ] Delta calculation is correct (to_add, to_remove, unchanged)
- [ ] Members are added when they join OUs
- [ ] Members are removed when they leave OUs
- [ ] Members already in group are not touched
- [ ] Sync statistics are stored in `last_sync_stats`
- [ ] `total_syncs` counter increments correctly
- [ ] Error handling works for failed additions/removals
- [ ] Rate limiting is respected (no API quota exceeded)

### Phase 4: Import/Export
- [ ] Export downloads valid JSON file
- [ ] Export includes all group configurations
- [ ] Export file contains correct metadata (version, date, domain)
- [ ] Import accepts exported JSON files
- [ ] Import validates file format before processing
- [ ] Import checks domain compatibility
- [ ] Import creates new configs for new groups
- [ ] Import updates existing configs
- [ ] Import with sync creates groups if missing
- [ ] Import with sync uses FULL SYNC for new groups
- [ ] Import with sync uses SMART SYNC for existing groups
- [ ] Import without sync only updates configs (no Google API calls)

### Phase 5: Full Sync All
- [ ] Full Sync All processes configs sequentially (not parallel)
- [ ] Each config uses SMART SYNC during Full Sync All
- [ ] Progress is visible during batch operation
- [ ] Results show success/failure for each group
- [ ] Errors don't stop the entire batch
- [ ] Confirmation dialog appears before starting
- [ ] Button is disabled during operation
- [ ] Configuration list refreshes after completion

### Phase 6: Translations
- [ ] All new UI elements have translations in EN/ES/PT
- [ ] Language switching works without errors
- [ ] Translations are grammatically correct
- [ ] Formatting (plurals, variables) works correctly
- [ ] No missing translation keys in console

### Integration Testing
- [ ] Create new group → performs FULL SYNC
- [ ] Re-sync existing group → performs SMART SYNC
- [ ] Add users to OU → smart sync adds them
- [ ] Remove users from OU → smart sync removes them
- [ ] Import config → syncs correctly based on group existence
- [ ] Export → Import → groups work as expected
- [ ] Full Sync All → all groups updated correctly
- [ ] Failed users are tracked and displayable
- [ ] Job queue shows accurate progress
- [ ] No memory leaks during long operations
- [ ] Backend logs show clear progress messages

---

## Code Examples

### GroupCard Component

```jsx
// frontend/src/components/GroupCard.jsx
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import './GroupCard.css'

function GroupCard({ config, onSync, onEdit, onDelete }) {
  const { t } = useTranslation()
  const [syncing, setSyncing] = useState(false)

  const handleSync = async () => {
    setSyncing(true)
    try {
      await onSync(config.config_uuid)
    } finally {
      setSyncing(false)
    }
  }

  const formatRelativeTime = (date) => {
    if (!date) return t('groupSync.neverSynced')

    const seconds = Math.floor((new Date() - new Date(date)) / 1000)
    if (seconds < 60) return t('common.justNow')
    if (seconds < 3600) return t('common.minutesAgo', { minutes: Math.floor(seconds / 60) })
    if (seconds < 86400) return t('common.hoursAgo', { hours: Math.floor(seconds / 3600) })
    return t('common.daysAgo', { days: Math.floor(seconds / 86400) })
  }

  const syncStats = config.last_sync_stats ? JSON.parse(config.last_sync_stats) : null

  return (
    <div className="group-card">
      <div className="group-header">
        <div className="group-icon">
          <span>📧</span>
        </div>
        <div className="group-info">
          <h3 className="group-email">{config.group_email}</h3>
          <p className="group-name">{config.group_name}</p>
        </div>
        <button
          className="btn-sync"
          onClick={handleSync}
          disabled={syncing}
        >
          {syncing ? '⏳' : '🔄'} {t('groupSync.resyncButton')}
        </button>
      </div>

      <div className="group-body">
        <div className="group-meta">
          <span className="meta-item">
            <strong>{config.ou_paths.length}</strong> {t('groupSync.ousInConfig')}
          </span>
          {config.last_synced_at && (
            <span className="meta-item">
              {t('groupSync.lastSynced')}: {formatRelativeTime(config.last_synced_at)}
            </span>
          )}
        </div>

        {syncStats && (
          <div className="sync-stats">
            <div className="stat-item stat-add">
              <span className="stat-icon">+</span>
              <span className="stat-value">{syncStats.added}</span>
              <span className="stat-label">{t('groupSync.syncStats.added')}</span>
            </div>
            <div className="stat-item stat-remove">
              <span className="stat-icon">-</span>
              <span className="stat-value">{syncStats.removed}</span>
              <span className="stat-label">{t('groupSync.syncStats.removed')}</span>
            </div>
            <div className="stat-item stat-unchanged">
              <span className="stat-icon">=</span>
              <span className="stat-value">{syncStats.unchanged}</span>
              <span className="stat-label">{t('groupSync.syncStats.unchanged')}</span>
            </div>
            {(syncStats.failed_add > 0 || syncStats.failed_remove > 0) && (
              <div className="stat-item stat-failed">
                <span className="stat-icon">✗</span>
                <span className="stat-value">{syncStats.failed_add + syncStats.failed_remove}</span>
                <span className="stat-label">{t('groupSync.syncStats.failed')}</span>
              </div>
            )}
          </div>
        )}

        {config.group_description && (
          <p className="group-description">{config.group_description}</p>
        )}
      </div>

      <div className="group-footer">
        <button className="btn-icon" onClick={() => onEdit(config)}>
          ✏️ {t('groupSync.editGroup')}
        </button>
        <button className="btn-icon btn-danger" onClick={() => onDelete(config.config_uuid)}>
          🗑️ {t('common.delete')}
        </button>
      </div>
    </div>
  )
}

export default GroupCard
```

### CompactJobQueue Component

```jsx
// frontend/src/components/CompactJobQueue.jsx
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import './CompactJobQueue.css'

function CompactJobQueue({ apiBaseUrl, jobType = 'group_sync', onViewAll }) {
  const { t } = useTranslation()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchJobs()
    const interval = setInterval(fetchJobs, 5000) // Refresh every 5s
    return () => clearInterval(interval)
  }, [])

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/batch/jobs?job_type=${jobType}`)
      // Show only active and recent jobs
      const activeJobs = response.data.jobs
        .filter(j => ['pending', 'running'].includes(j.status))
        .slice(0, 3)
      setJobs(activeJobs)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return '⏳'
      case 'running': return '▶️'
      case 'completed': return '✅'
      case 'failed': return '❌'
      default: return '❓'
    }
  }

  if (jobs.length === 0) {
    return (
      <div className="compact-job-queue">
        <h4>{t('groupSync.activeJobs')}</h4>
        <p className="no-jobs">{t('groupSync.noActiveJobs')}</p>
      </div>
    )
  }

  return (
    <div className="compact-job-queue">
      <h4>{t('groupSync.activeJobs')}</h4>

      <div className="job-list">
        {jobs.map(job => (
          <div key={job.job_uuid} className="compact-job-item">
            <div className="job-header">
              <span className="job-status-icon">{getStatusIcon(job.status)}</span>
              <span className="job-id">#{job.job_uuid.slice(0, 8)}</span>
              <span className="job-status">{t(`groupSync.status.${job.status}`)}</span>
            </div>

            <div className="job-progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${job.progress_percentage}%`,
                  backgroundColor: job.status === 'failed' ? '#f44336' : '#4caf50'
                }}
              />
            </div>

            <div className="job-details">
              <span className="job-progress-text">
                {Math.round(job.progress_percentage)}% • {job.processed_users}/{job.total_users}
              </span>
            </div>
          </div>
        ))}
      </div>

      {onViewAll && (
        <button className="btn-view-all" onClick={onViewAll}>
          {t('groupSync.viewAllJobs')}
        </button>
      )}
    </div>
  )
}

export default CompactJobQueue
```

---

## Quick Reference

### Current System State
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:3000
- **Database:** `/Users/rafaelteodoro/Workspace/DEA-toolbox/backend/data/dea_toolbox.db`
- **Logs:** `backend/backend.log`

### Useful Commands

**Backend:**
```bash
cd /Users/rafaelteodoro/Workspace/DEA-toolbox/backend
source venv/bin/activate
python3 main.py
```

**Frontend:**
```bash
cd /Users/rafaelteodoro/Workspace/DEA-toolbox/frontend
npm run dev
```

**Check Running Services:**
```bash
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
```

**View Backend Logs:**
```bash
tail -f backend/backend.log
```

**Database Migration:**
```bash
cd backend
python3 migrations/add_smart_sync_fields.py
```

### Key Files Reference

**Backend:**
- `backend/main.py` - API endpoints
- `backend/services/group_sync_processor.py` - Sync logic
- `backend/services/google_workspace.py` - Google API wrapper
- `backend/database/models.py` - Database models

**Frontend:**
- `frontend/src/components/OUGroupSync.jsx` - Main component
- `frontend/src/components/Sidebar.jsx` - Navigation
- `frontend/src/locales/` - Translations

---

## Success Criteria

### Must Have (MVP)
✅ All critical bugs fixed
✅ Smart sync engine working
✅ First-time sync = FULL, subsequent = SMART
✅ Import/Export functionality
✅ Full Sync All feature
✅ Improved UI with better layout

### Nice to Have
⭐ Real-time progress updates
⭐ Sync history/logs viewer
⭐ Group member preview before sync
⭐ Scheduling for automatic syncs
⭐ Email notifications on sync completion

---

## Notes & Decisions

1. **Sync Strategy Decision:**
   - First sync = FULL (add only, no remove)
   - Subsequent = SMART (delta: add + remove)
   - Reason: Prevents accidental mass removal on first run

2. **Import Behavior:**
   - New group (not in Google) → Create + FULL SYNC
   - Existing group (in Google) → SMART SYNC
   - Reason: Matches first-time vs subsequent sync logic

3. **Full Sync All:**
   - Always uses SMART SYNC (not FULL)
   - Processes sequentially (not parallel)
   - Reason: Prevents API rate limiting, allows monitoring

4. **Rate Limiting:**
   - 33ms delay between API calls (~30 calls/sec)
   - Stay well below Google's 100 QPS limit
   - Reason: Avoid quota exhaustion

5. **Error Handling:**
   - "Already a member" is not an error
   - Track failed operations but continue processing
   - Reason: Resilience and complete data

---

## Contact & Support

**Project:** DEA Toolbox
**Repository:** /Users/rafaelteodoro/Workspace/DEA-toolbox
**Developer:** Rafael Teodoro

Good luck with the implementation! 🚀
