"""
Migration script to add group sync columns to batch_jobs and create group_sync_operations table
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'data', 'dea_toolbox.db')

print(f"Migrating database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if group_name_pattern column already exists
    cursor.execute("PRAGMA table_info(batch_jobs)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'group_name_pattern' not in columns:
        print("Adding new columns to batch_jobs table...")

        # Add new columns for group sync
        cursor.execute("ALTER TABLE batch_jobs ADD COLUMN group_name_pattern VARCHAR(255)")
        cursor.execute("ALTER TABLE batch_jobs ADD COLUMN group_description TEXT")
        cursor.execute("ALTER TABLE batch_jobs ADD COLUMN created_groups TEXT")

        print("✓ New columns added to batch_jobs")
    else:
        print("✓ Columns already exist in batch_jobs")

    # Check if group_sync_operations table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='group_sync_operations'")
    table_exists = cursor.fetchone()

    if not table_exists:
        print("Creating group_sync_operations table...")

        cursor.execute("""
            CREATE TABLE group_sync_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_uuid VARCHAR(36) NOT NULL,
                ou_path VARCHAR(500) NOT NULL,
                ou_name VARCHAR(255) NOT NULL,
                group_email VARCHAR(255) NOT NULL,
                group_name VARCHAR(255) NOT NULL,
                status VARCHAR(20) NOT NULL,
                total_members INTEGER DEFAULT 0,
                synced_members INTEGER DEFAULT 0,
                failed_members INTEGER DEFAULT 0,
                group_created BOOLEAN DEFAULT 0,
                error_message TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (job_uuid) REFERENCES batch_jobs (job_uuid)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX idx_group_sync_job_uuid ON group_sync_operations(job_uuid)")

        print("✓ group_sync_operations table created")
    else:
        print("✓ group_sync_operations table already exists")

    conn.commit()
    print("✓ Migration completed successfully!")

except Exception as e:
    print(f"✗ Migration failed: {e}")
    conn.rollback()
    raise
finally:
    conn.close()
