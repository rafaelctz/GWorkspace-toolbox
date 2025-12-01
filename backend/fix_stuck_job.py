#!/usr/bin/env python3
"""
Fix stuck jobs that are in 'running' state but not actually processing
This can happen if the backend is killed while a job is running
"""
import sys
from database.session import SessionLocal
from database.models import BatchJob, CachedUser
from sqlalchemy import func

def fix_stuck_jobs():
    """Reset stuck jobs from 'running' to 'pending' so they can be restarted"""
    db = SessionLocal()
    try:
        # Find all jobs that are stuck in 'running' state
        stuck_jobs = db.query(BatchJob).filter(
            BatchJob.status == 'running'
        ).all()

        if not stuck_jobs:
            print("No stuck jobs found")
            return

        print(f"Found {len(stuck_jobs)} stuck job(s) in 'running' state:\n")

        for job in stuck_jobs:
            print(f"Job UUID: {job.job_uuid}")
            print(f"  Status: {job.status}")
            print(f"  Total users: {job.total_users}")
            print(f"  Processed: {job.processed_users}/{job.total_users}")
            print(f"  Successful: {job.successful_users}")
            print(f"  Failed: {job.failed_users}")
            print(f"  Started: {job.started_at}")
            print(f"  Attribute: {job.attribute} = {job.value}")

            # Check user statuses
            user_counts = db.query(
                CachedUser.status,
                func.count(CachedUser.id)
            ).filter(
                CachedUser.job_uuid == job.job_uuid
            ).group_by(CachedUser.status).all()

            print(f"  User statuses: {dict(user_counts)}")

            # Reset any users in 'processing' state back to 'pending'
            processing_users = db.query(CachedUser).filter(
                CachedUser.job_uuid == job.job_uuid,
                CachedUser.status == 'processing'
            ).all()

            if processing_users:
                print(f"  Resetting {len(processing_users)} users from 'processing' to 'pending'")
                for user in processing_users:
                    user.status = 'pending'

            # Reset job to pending
            job.status = 'pending'
            job.started_at = None
            job.completed_at = None

            print(f"  ✓ Reset job to 'pending' state\n")

        # Commit changes
        db.commit()
        print(f"✓ All stuck jobs have been reset and can now be restarted")

    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    fix_stuck_jobs()
