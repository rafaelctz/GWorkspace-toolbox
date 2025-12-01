"""Service for caching users from organizational units before batch processing"""
import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from database.models import CachedUser, BatchJob
from services.google_workspace import GoogleWorkspaceService


class UserCacheService:
    """Handles user caching from Google Workspace OUs"""

    def __init__(self, db: Session, google_service: GoogleWorkspaceService):
        self.db = db
        self.google_service = google_service

    def fetch_and_cache_users(self, job_uuid: str, ou_paths: List[str]) -> Dict:
        """
        Fetch users from specified OUs and cache them in database

        Args:
            job_uuid: The batch job UUID to associate users with
            ou_paths: List of organizational unit paths to fetch users from

        Returns:
            Dict with total_users, cached_users, and any errors
        """
        if not self.google_service.is_authenticated():
            raise Exception("Google Workspace service not authenticated")

        cached_count = 0
        errors = []
        user_emails_seen = set()  # Deduplicate users

        try:
            for ou_path in ou_paths:
                try:
                    # Fetch users from this OU
                    users = self._fetch_users_from_ou(ou_path)

                    # Cache each user
                    for user in users:
                        user_email = user.get('primaryEmail')

                        # Skip if already cached (avoid duplicates)
                        if user_email in user_emails_seen:
                            continue

                        user_emails_seen.add(user_email)

                        # Create cached user record
                        cached_user = CachedUser(
                            job_uuid=job_uuid,
                            email=user_email,
                            ou_path=user.get('orgUnitPath', ou_path),
                            user_data=json.dumps(user),  # Store full user profile
                            status='pending'
                        )
                        self.db.add(cached_user)
                        cached_count += 1

                    # Commit after each OU to avoid losing progress
                    self.db.commit()

                except Exception as e:
                    error_msg = f"Error fetching users from {ou_path}: {str(e)}"
                    errors.append(error_msg)
                    print(f"⚠️  {error_msg}")

            return {
                'total_users': cached_count,
                'cached_users': cached_count,
                'errors': errors
            }

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to cache users: {str(e)}")

    def _fetch_users_from_ou(self, ou_path: str) -> List[Dict]:
        """
        Fetch all users from a specific organizational unit

        Args:
            ou_path: The OU path to fetch users from

        Returns:
            List of user dictionaries
        """
        users = []
        page_token = None

        try:
            while True:
                # Try query-based filtering first (more efficient)
                params = {
                    'customer': 'my_customer',
                    'maxResults': 500,  # Max allowed by API
                    'projection': 'full',
                    'query': f'orgUnitPath={ou_path}'
                }

                if page_token:
                    params['pageToken'] = page_token

                results = self.google_service.service.users().list(**params).execute()

                batch_users = results.get('users', [])
                users.extend(batch_users)

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

        except Exception as e:
            # Fallback: fetch all users and filter client-side
            print(f"Query filtering failed for {ou_path}, using client-side filtering")
            users = self._fetch_users_client_side_filter(ou_path)

        return users

    def _fetch_users_client_side_filter(self, ou_path: str) -> List[Dict]:
        """
        Fallback method: fetch all users and filter by OU client-side

        Args:
            ou_path: The OU path to filter by

        Returns:
            List of user dictionaries
        """
        users = []
        page_token = None

        while True:
            params = {
                'customer': 'my_customer',
                'maxResults': 500,
                'projection': 'full'
            }

            if page_token:
                params['pageToken'] = page_token

            results = self.google_service.service.users().list(**params).execute()

            # Filter users by OU path (include sub-OUs)
            for user in results.get('users', []):
                user_ou = user.get('orgUnitPath', '')
                if user_ou == ou_path or user_ou.startswith(ou_path + '/'):
                    users.append(user)

            page_token = results.get('nextPageToken')
            if not page_token:
                break

        return users

    def get_cached_users(self, job_uuid: str, status: Optional[str] = None) -> List[CachedUser]:
        """
        Get cached users for a job

        Args:
            job_uuid: The batch job UUID
            status: Optional filter by status (pending, processing, success, failed)

        Returns:
            List of CachedUser objects
        """
        query = self.db.query(CachedUser).filter(CachedUser.job_uuid == job_uuid)

        if status:
            query = query.filter(CachedUser.status == status)

        return query.all()

    def update_user_status(
        self,
        job_uuid: str,
        email: str,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update the status of a cached user

        Args:
            job_uuid: The batch job UUID
            email: User email
            status: New status (processing, success, failed)
            error_message: Optional error message for failed status
        """
        from datetime import datetime

        user = self.db.query(CachedUser).filter(
            CachedUser.job_uuid == job_uuid,
            CachedUser.email == email
        ).first()

        if user:
            user.status = status
            user.error_message = error_message
            user.processed_at = datetime.utcnow()
            self.db.commit()

    def get_user_count(self, job_uuid: str) -> Dict[str, int]:
        """
        Get counts of users by status

        Args:
            job_uuid: The batch job UUID

        Returns:
            Dict with counts: total, pending, processing, success, failed
        """
        from sqlalchemy import func

        counts = self.db.query(
            CachedUser.status,
            func.count(CachedUser.id)
        ).filter(
            CachedUser.job_uuid == job_uuid
        ).group_by(
            CachedUser.status
        ).all()

        result = {
            'total': 0,
            'pending': 0,
            'processing': 0,
            'success': 0,
            'failed': 0
        }

        for status, count in counts:
            result[status] = count
            result['total'] += count

        return result
