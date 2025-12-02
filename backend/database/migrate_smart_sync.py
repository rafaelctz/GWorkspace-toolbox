"""
Migration script to add smart sync fields to GroupSyncConfig table

Run this script to update an existing database with the new smart sync fields.
Usage: python3 backend/database/migrate_smart_sync.py
"""
import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to path to import session
sys.path.insert(0, str(Path(__file__).parent.parent))
from database.session import DATABASE_PATH


def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)


def migrate_smart_sync_fields():
    """Add smart sync fields to group_sync_configs table"""
    print(f"[Migration] Connecting to database: {DATABASE_PATH}")

    if not os.path.exists(DATABASE_PATH):
        print(f"[Migration] Database does not exist yet. It will be created with all fields on first run.")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='group_sync_configs'")
        if not cursor.fetchone():
            print("[Migration] Table 'group_sync_configs' does not exist yet. Skipping migration.")
            conn.close()
            return

        migrations_applied = 0

        # Add is_first_sync column
        if not check_column_exists(cursor, 'group_sync_configs', 'is_first_sync'):
            print("[Migration] Adding column 'is_first_sync'...")
            cursor.execute("""
                ALTER TABLE group_sync_configs
                ADD COLUMN is_first_sync INTEGER DEFAULT 1
            """)
            migrations_applied += 1
        else:
            print("[Migration] Column 'is_first_sync' already exists")

        # Add last_sync_stats column
        if not check_column_exists(cursor, 'group_sync_configs', 'last_sync_stats'):
            print("[Migration] Adding column 'last_sync_stats'...")
            cursor.execute("""
                ALTER TABLE group_sync_configs
                ADD COLUMN last_sync_stats TEXT
            """)
            migrations_applied += 1
        else:
            print("[Migration] Column 'last_sync_stats' already exists")

        # Add total_syncs column
        if not check_column_exists(cursor, 'group_sync_configs', 'total_syncs'):
            print("[Migration] Adding column 'total_syncs'...")
            cursor.execute("""
                ALTER TABLE group_sync_configs
                ADD COLUMN total_syncs INTEGER DEFAULT 0
            """)
            migrations_applied += 1
        else:
            print("[Migration] Column 'total_syncs' already exists")

        # Add imported_from_file column
        if not check_column_exists(cursor, 'group_sync_configs', 'imported_from_file'):
            print("[Migration] Adding column 'imported_from_file'...")
            cursor.execute("""
                ALTER TABLE group_sync_configs
                ADD COLUMN imported_from_file INTEGER DEFAULT 0
            """)
            migrations_applied += 1
        else:
            print("[Migration] Column 'imported_from_file' already exists")

        # Add import_date column
        if not check_column_exists(cursor, 'group_sync_configs', 'import_date'):
            print("[Migration] Adding column 'import_date'...")
            cursor.execute("""
                ALTER TABLE group_sync_configs
                ADD COLUMN import_date DATETIME
            """)
            migrations_applied += 1
        else:
            print("[Migration] Column 'import_date' already exists")

        conn.commit()
        print(f"\n[Migration] Complete! Applied {migrations_applied} new columns.")

        if migrations_applied == 0:
            print("[Migration] All smart sync fields already exist. No changes needed.")

    except Exception as e:
        conn.rollback()
        print(f"[Migration] ERROR: {str(e)}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Smart Sync Migration Script")
    print("=" * 60)
    migrate_smart_sync_fields()
    print("=" * 60)
