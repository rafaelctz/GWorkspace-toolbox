"""Service for batch processing attribute injections"""
import json
import uuid
import time
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from googleapiclient.errors import HttpError

from database.models import BatchJob, CachedUser, BatchOperation
from services.google_workspace import GoogleWorkspaceService
from services.user_cache_service import UserCacheService
from services.api_retry import APIRetryHandler


class BatchProcessor:
    """Handles batch processing of attribute injections with progress tracking"""

    BATCH_SIZE = 25  # Reduced from 50 to 25 for better rate limiting
    API_CALL_DELAY = 0.033  # 33ms delay between API calls (~30 calls/sec, safe under 40/sec limit)
    PROGRESS_COMMIT_INTERVAL = 5  # Commit progress every 5 users for real-time UI updates

    def __init__(self, db: Session, google_service: GoogleWorkspaceService):
        self.db = db
        self.google_service = google_service
        self.user_cache_service = UserCacheService(db, google_service)
        self.retry_handler = APIRetryHandler(max_retries=5, base_delay=1.0)

    def create_job(
        self,
        ou_paths: List[str],
        attribute: str,
        value: str
    ) -> BatchJob:
        """
        Create a new batch job and cache users

        Args:
            ou_paths: List of organizational unit paths
            attribute: Attribute name to inject
            value: Value to set

        Returns:
            BatchJob object
        """
        # Generate unique job ID
        job_uuid = str(uuid.uuid4())

        # Create job record
        job = BatchJob(
            job_uuid=job_uuid,
            job_type='attribute_injection',
            status='pending',
            ou_paths=json.dumps(ou_paths),
            attribute=attribute,
            value=value,
            total_users=0,
            processed_users=0,
            successful_users=0,
            failed_users=0,
            progress_percentage=0.0
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        # Fetch and cache users from OUs
        try:
            cache_result = self.user_cache_service.fetch_and_cache_users(
                job_uuid=job_uuid,
                ou_paths=ou_paths
            )

            # Update job with total user count
            job.total_users = cache_result['total_users']
            self.db.commit()

            return job

        except Exception as e:
            # Mark job as failed if caching fails
            job.status = 'failed'
            job.error_message = f"Failed to cache users: {str(e)}"
            self.db.commit()
            raise

    def process_job(self, job_uuid: str) -> Dict:
        """
        Process a batch job asynchronously

        Args:
            job_uuid: The job UUID to process

        Returns:
            Dict with processing results
        """
        print(f"[BatchProcessor] Starting process_job for {job_uuid}")

        # Get job
        job = self.db.query(BatchJob).filter(
            BatchJob.job_uuid == job_uuid
        ).first()

        if not job:
            print(f"[BatchProcessor] ERROR: Job {job_uuid} not found")
            raise Exception(f"Job {job_uuid} not found")

        if job.status != 'pending':
            print(f"[BatchProcessor] ERROR: Job {job_uuid} status is {job.status}, not pending")
            raise Exception(f"Job {job_uuid} is not in pending state")

        try:
            # Mark job as running
            print(f"[BatchProcessor] Marking job as running")
            job.status = 'running'
            job.started_at = datetime.utcnow()
            self.db.commit()

            # Get all pending users
            print(f"[BatchProcessor] Fetching pending users")
            users = self.user_cache_service.get_cached_users(
                job_uuid=job_uuid,
                status='pending'
            )
            print(f"[BatchProcessor] Found {len(users)} pending users")

            if not users:
                print(f"[BatchProcessor] No users to process, marking as completed")
                job.status = 'completed'
                job.completed_at = datetime.utcnow()
                job.progress_percentage = 100.0
                self.db.commit()
                return {
                    'status': 'completed',
                    'message': 'No users to process'
                }

            # Split users into batches
            batches = self._create_batches(users)
            print(f"[BatchProcessor] Created {len(batches)} batches of up to {self.BATCH_SIZE} users each")

            # Process each batch
            for batch_number, user_batch in enumerate(batches, start=1):
                print(f"[BatchProcessor] ========== Processing batch {batch_number}/{len(batches)} ==========")

                # Refresh credentials before each batch to prevent token expiration
                print(f"[BatchProcessor] Refreshing credentials before batch {batch_number}")
                try:
                    self._ensure_valid_credentials()
                    print(f"[BatchProcessor] Credentials refreshed successfully")
                except Exception as cred_error:
                    print(f"[BatchProcessor] ERROR refreshing credentials: {str(cred_error)}")
                    raise

                print(f"[BatchProcessor] Processing {len(user_batch)} users in batch {batch_number}")
                try:
                    self._process_batch(
                        job=job,
                        batch_number=batch_number,
                        users=user_batch
                    )
                    print(f"[BatchProcessor] Batch {batch_number} completed successfully")
                except Exception as batch_error:
                    print(f"[BatchProcessor] ERROR processing batch {batch_number}: {str(batch_error)}")
                    raise

            # Mark job as completed
            print(f"[BatchProcessor] All batches completed, marking job as completed")
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.progress_percentage = 100.0
            self.db.commit()

            print(f"[BatchProcessor] Job completed: {job.successful_users} successful, {job.failed_users} failed")
            return {
                'status': 'completed',
                'total_users': job.total_users,
                'successful_users': job.successful_users,
                'failed_users': job.failed_users
            }

        except Exception as e:
            # Mark job as failed
            print(f"[BatchProcessor] FATAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    def _create_batches(self, users: List[CachedUser]) -> List[List[CachedUser]]:
        """Split users into batches"""
        batches = []
        for i in range(0, len(users), self.BATCH_SIZE):
            batches.append(users[i:i + self.BATCH_SIZE])
        return batches

    def _ensure_valid_credentials(self) -> None:
        """
        Ensure credentials are valid and refresh if needed.
        This prevents token expiration during long-running jobs.
        """
        print(f"[BatchProcessor] Checking credential validity...")
        try:
            # For service accounts, credentials don't expire but we can refresh the service
            if hasattr(self.google_service, 'creds') and self.google_service.creds:
                print(f"[BatchProcessor] Credentials object exists: {type(self.google_service.creds)}")

                # Check if credentials have a refresh method
                if hasattr(self.google_service.creds, 'refresh') and hasattr(self.google_service.creds, 'expired'):
                    print(f"[BatchProcessor] OAuth credentials detected")
                    # For OAuth credentials, check if expired and refresh
                    if self.google_service.creds.expired:
                        print(f"[BatchProcessor] Credentials expired, refreshing...")
                        if self.google_service.creds.refresh_token:
                            from google.auth.transport.requests import Request
                            self.google_service.creds.refresh(Request())
                            print(f"[BatchProcessor] OAuth credentials refreshed successfully")
                        else:
                            print(f"[BatchProcessor] WARNING: No refresh token available")
                    else:
                        print(f"[BatchProcessor] OAuth credentials still valid")
                # For service accounts with delegation, recreate credentials
                elif hasattr(self.google_service.creds, 'with_subject'):
                    print(f"[BatchProcessor] Service account credentials detected (auto-refreshed by library)")
                else:
                    print(f"[BatchProcessor] Unknown credential type")
            else:
                print(f"[BatchProcessor] WARNING: No credentials object found!")
        except Exception as e:
            # Log but don't fail - credentials might still be valid
            print(f"[BatchProcessor] WARNING: Could not refresh credentials: {str(e)}")
            import traceback
            traceback.print_exc()

    def _process_batch(
        self,
        job: BatchJob,
        batch_number: int,
        users: List[CachedUser]
    ) -> None:
        """
        Process a single batch of users

        Args:
            job: The BatchJob object
            batch_number: The batch number
            users: List of CachedUser objects to process
        """
        print(f"[BatchProcessor] _process_batch started for batch {batch_number}")

        # Create batch operation record
        batch_op = BatchOperation(
            job_uuid=job.job_uuid,
            batch_number=batch_number,
            user_emails=json.dumps([u.email for u in users]),
            status='running',
            started_at=datetime.utcnow()
        )
        self.db.add(batch_op)
        self.db.commit()
        print(f"[BatchProcessor] Batch operation record created")

        # Process each user in the batch
        success_count = 0
        fail_count = 0
        for idx, user in enumerate(users, 1):
            try:
                # Mark user as processing (no commit yet)
                user.status = 'processing'

                # Inject attribute with rate limiting
                self._inject_attribute_to_user(
                    user_email=user.email,
                    attribute=job.attribute,
                    value=job.value
                )

                # Rate limiting: delay after each API call
                time.sleep(self.API_CALL_DELAY)

                # Mark user as success
                user.status = 'success'
                user.error_message = None

                # Update job counters
                job.successful_users += 1
                success_count += 1

            except Exception as e:
                # Mark user as failed
                error_msg = str(e)[:200]  # Limit error message length
                user.status = 'failed'
                user.error_message = error_msg

                # Update job counters
                job.failed_users += 1
                fail_count += 1
                print(f"[BatchProcessor] User {user.email} failed: {error_msg}")

            # Update progress
            job.processed_users += 1
            job.progress_percentage = (job.processed_users / job.total_users) * 100

            # Commit progress every N users for real-time UI updates
            if idx % self.PROGRESS_COMMIT_INTERVAL == 0:
                self.db.commit()
                print(f"[BatchProcessor] Batch {batch_number}: Progress committed - {idx}/{len(users)} users ({job.progress_percentage:.1f}% overall)")

            # Log progress every 10 users
            elif idx % 10 == 0:
                print(f"[BatchProcessor] Batch {batch_number}: Processed {idx}/{len(users)} users")

        # Mark batch as completed
        batch_op.status = 'completed'
        batch_op.completed_at = datetime.utcnow()

        print(f"[BatchProcessor] Batch {batch_number} summary: {success_count} successful, {fail_count} failed")
        print(f"[BatchProcessor] Overall progress: {job.processed_users}/{job.total_users} ({job.progress_percentage:.1f}%)")

        # Final commit for the batch
        print(f"[BatchProcessor] Committing final batch {batch_number} to database...")
        self.db.commit()
        print(f"[BatchProcessor] Batch {batch_number} committed successfully")

    def _inject_attribute_to_user(
        self,
        user_email: str,
        attribute: str,
        value: str
    ) -> None:
        """
        Inject attribute to a single user

        Args:
            user_email: User's email address
            attribute: Attribute name
            value: Value to set

        Raises:
            Exception if injection fails
        """
        try:
            # Handle complex organization attributes
            if attribute in ['title', 'department', 'employeeType', 'costCenter']:
                # Map attribute to correct field
                field_mapping = {
                    'title': 'title',
                    'department': 'department',
                    'employeeType': 'type',
                    'costCenter': 'costCenter'
                }

                # Create organization object directly without fetching
                update_body = {
                    'organizations': [{
                        field_mapping[attribute]: value,
                        'primary': True
                    }]
                }

            elif attribute == 'buildingId':
                # Handle location/building
                update_body = {
                    'locations': [{
                        'type': 'desk',
                        'area': 'desk',
                        'buildingId': value
                    }]
                }

            elif attribute == 'manager':
                # Handle manager as relation
                update_body = {
                    'relations': [{
                        'type': 'manager',
                        'value': value
                    }]
                }

            else:
                # For any other standard attribute, use directly
                update_body = {attribute: value}

            # Update the user with retry logic for SSL and transient errors
            def execute_update():
                return self.google_service.service.users().update(
                    userKey=user_email,
                    body=update_body
                ).execute()

            self.retry_handler.execute_with_retry(execute_update)

        except HttpError as error:
            raise Exception(f"Google API error: {str(error)}")
        except Exception as error:
            raise Exception(f"Error injecting attribute: {str(error)}")

    def get_job_status(self, job_uuid: str) -> Dict:
        """
        Get detailed status of a job

        Args:
            job_uuid: The job UUID

        Returns:
            Dict with job status and progress
        """
        job = self.db.query(BatchJob).filter(
            BatchJob.job_uuid == job_uuid
        ).first()

        if not job:
            raise Exception(f"Job {job_uuid} not found")

        # Get user counts by status
        user_counts = self.user_cache_service.get_user_count(job_uuid)

        return {
            'job_uuid': job.job_uuid,
            'status': job.status,
            'ou_paths': json.loads(job.ou_paths),
            'attribute': job.attribute,
            'value': job.value,
            'total_users': job.total_users,
            'processed_users': job.processed_users,
            'successful_users': job.successful_users,
            'failed_users': job.failed_users,
            'progress_percentage': job.progress_percentage,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message,
            'user_status_counts': user_counts
        }

    def get_all_jobs(self, limit: int = 50) -> List[Dict]:
        """
        Get all jobs ordered by creation date

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of job status dicts
        """
        jobs = self.db.query(BatchJob).order_by(
            BatchJob.created_at.desc()
        ).limit(limit).all()

        return [self.get_job_status(job.job_uuid) for job in jobs]

    def get_failed_users(self, job_uuid: str) -> List[Dict]:
        """
        Get all failed users for a job with their error messages

        Args:
            job_uuid: The job UUID

        Returns:
            List of dicts with user email and error message
        """
        failed_users = self.user_cache_service.get_cached_users(
            job_uuid=job_uuid,
            status='failed'
        )

        return [
            {
                'email': user.email,
                'error_message': user.error_message,
                'ou_path': user.ou_path
            }
            for user in failed_users
        ]
