"""
Migration script to make batch_jobs columns nullable for multiple job types
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'data', 'dea_toolbox.db')

print(f"Migrating database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Backup existing data
    print("Backing up existing batch_jobs data...")
    cursor.execute("SELECT * FROM batch_jobs")
    existing_data = cursor.fetchall()
    print(f"Found {len(existing_data)} existing jobs")

    # Get column names
    cursor.execute("PRAGMA table_info(batch_jobs)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Columns: {columns}")

    # Drop the old table
    print("Dropping old batch_jobs table...")
    cursor.execute("DROP TABLE IF EXISTS batch_jobs")

    # Create new table with nullable columns
    print("Creating new batch_jobs table with nullable columns...")
    cursor.execute("""
        CREATE TABLE batch_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_uuid VARCHAR(36) UNIQUE NOT NULL,
            job_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL,
            ou_paths TEXT,
            attribute VARCHAR(100),
            value TEXT,
            file_path TEXT,
            total_users INTEGER DEFAULT 0,
            processed_users INTEGER DEFAULT 0,
            successful_users INTEGER DEFAULT 0,
            failed_users INTEGER DEFAULT 0,
            progress_percentage REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT
        )
    """)

    # Create indexes
    print("Creating indexes...")
    cursor.execute("CREATE INDEX idx_batch_jobs_job_uuid ON batch_jobs(job_uuid)")
    cursor.execute("CREATE INDEX idx_batch_jobs_status ON batch_jobs(status)")

    # Restore data if any existed
    if existing_data:
        print(f"Restoring {len(existing_data)} jobs...")
        placeholders = ','.join(['?' for _ in columns])
        cursor.executemany(f"INSERT INTO batch_jobs ({','.join(columns)}) VALUES ({placeholders})", existing_data)

    conn.commit()
    print("✓ Migration completed successfully!")

except Exception as e:
    print(f"✗ Migration failed: {e}")
    conn.rollback()
    raise
finally:
    conn.close()
