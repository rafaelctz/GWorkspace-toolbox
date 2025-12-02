"""Service for batch processing OU to Group synchronization"""
import json
import uuid
import time
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session

from database.models import BatchJob, GroupSyncConfig
from services.google_workspace import GoogleWorkspaceService


class GroupSyncProcessor:
    """Handles batch processing of OU to Group synchronization with progress tracking"""

    API_CALL_DELAY = 0.033  # 33ms delay between API calls (~30 calls/sec)

    def __init__(self, db: Session, google_service: GoogleWorkspaceService):
        self.db = db
        self.google_service = google_service

    def create_or_update_config(
        self,
        ou_paths: List[str],
        group_email: str,
        group_name: str,
        group_description: str,
        domain: str,
        config_uuid: str = None
    ) -> GroupSyncConfig:
        """
        Create or update a saved group sync configuration

        Args:
            ou_paths: List of organizational unit paths
            group_email: Full email address for the group (e.g., 'alunos@domain.com')
            group_name: Display name for the group
            group_description: Description for the group
            domain: Domain for the workspace
            config_uuid: Optional UUID for updating existing config

        Returns:
            GroupSyncConfig object
        """
        if config_uuid:
            # Update existing config
            config = self.db.query(GroupSyncConfig).filter(
                GroupSyncConfig.config_uuid == config_uuid
            ).first()

            if not config:
                raise Exception(f"Config {config_uuid} not found")

            config.ou_paths = json.dumps(ou_paths)
            config.group_email = group_email
            config.group_name = group_name
            config.group_description = group_description
            config.domain = domain
            config.updated_at = datetime.utcnow()
        else:
            # Create new config
            config_uuid = str(uuid.uuid4())
            config = GroupSyncConfig(
                config_uuid=config_uuid,
                group_email=group_email,
                group_name=group_name,
                group_description=group_description,
                ou_paths=json.dumps(ou_paths),
                domain=domain
            )
            self.db.add(config)

        self.db.commit()
        self.db.refresh(config)
        return config

    def create_sync_job(self, config_uuid: str) -> BatchJob:
        """
        Create a new sync job from a saved configuration

        Args:
            config_uuid: The configuration UUID to sync

        Returns:
            BatchJob object
        """
        # Get the config
        config = self.db.query(GroupSyncConfig).filter(
            GroupSyncConfig.config_uuid == config_uuid
        ).first()

        if not config:
            raise Exception(f"Config {config_uuid} not found")

        job_uuid = str(uuid.uuid4())

        # Create job record
        # Store config_uuid in attribute field for later reference
        job = BatchJob(
            job_uuid=job_uuid,
            job_type='group_sync',
            status='pending',
            ou_paths=config.ou_paths,  # Store as JSON
            attribute=config_uuid,  # Store config_uuid here for routing to smart_sync
            group_name_pattern=config.group_email,  # Reuse field to store group_email
            group_description=config.group_description,
            created_groups=json.dumps([]),
            total_users=0,
            processed_users=0,
            successful_users=0,
            failed_users=0,
            progress_percentage=0.0
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def process_job(self, job_uuid: str) -> Dict:
        """
        Process a group sync job asynchronously
        Routes to smart_sync() or full_sync() based on config.is_first_sync

        Args:
            job_uuid: The job UUID to process

        Returns:
            Dict with processing results
        """
        print(f"[GroupSyncProcessor] Starting process_job for {job_uuid}")

        # Get job
        job = self.db.query(BatchJob).filter(
            BatchJob.job_uuid == job_uuid
        ).first()

        if not job:
            raise Exception(f"Job {job_uuid} not found")

        if job.status != 'pending':
            raise Exception(f"Job {job_uuid} is not in pending state")

        # Check if we have a config_uuid (stored in attribute field)
        config_uuid = job.attribute

        if config_uuid:
            # Get the config to check is_first_sync
            config = self.db.query(GroupSyncConfig).filter(
                GroupSyncConfig.config_uuid == config_uuid
            ).first()

            if config and not config.is_first_sync:
                # Use smart sync for subsequent syncs
                print(f"[GroupSyncProcessor] Routing to smart_sync (subsequent sync)")
                return self.smart_sync(config_uuid, job_uuid)
            else:
                print(f"[GroupSyncProcessor] Routing to full_sync (first sync)")
        else:
            print(f"[GroupSyncProcessor] No config_uuid, using full_sync")

        try:
            # Mark job as running
            job.status = 'running'
            job.started_at = datetime.utcnow()
            self.db.commit()

            # Parse OU paths and group info
            ou_paths = json.loads(job.ou_paths) if job.ou_paths else []
            group_email = job.group_name_pattern  # Stored in this field
            group_name = group_email.split('@')[0].replace('-', ' ').title()  # Generate from email
            group_description = job.group_description or f"Synchronized group"

            if not ou_paths:
                job.status = 'completed'
                job.completed_at = datetime.utcnow()
                job.progress_percentage = 100.0
                self.db.commit()
                return {'status': 'completed', 'message': 'No OUs to process'}

            print(f"[GroupSyncProcessor] Syncing {len(ou_paths)} OUs to group {group_email}")

            # Step 1: Create or get the group
            existing_group = self.google_service.get_group(group_email)

            if existing_group:
                print(f"[GroupSyncProcessor] Group already exists: {group_email}")
            else:
                print(f"[GroupSyncProcessor] Creating group: {group_email}")
                self.google_service.create_group(
                    group_email=group_email,
                    group_name=group_name,
                    description=group_description
                )
                time.sleep(self.API_CALL_DELAY)

            # Step 2: Collect all users from all OUs
            all_users = []
            for idx, ou_path in enumerate(ou_paths, 1):
                print(f"[GroupSyncProcessor] Getting users from OU {idx}/{len(ou_paths)}: {ou_path}")
                try:
                    users = self.google_service.get_users_in_ou(ou_path)
                    all_users.extend(users)
                    print(f"[GroupSyncProcessor] Found {len(users)} users in {ou_path}")
                except Exception as e:
                    print(f"[GroupSyncProcessor] Failed to get users from {ou_path}: {str(e)}")

            # Remove duplicates (users in multiple OUs)
            unique_users = {user['email']: user for user in all_users}.values()
            total_users = len(unique_users)

            job.total_users = total_users
            self.db.commit()

            print(f"[GroupSyncProcessor] Total unique users to sync: {total_users}")

            # Step 3: Add each user to the group
            synced = 0
            failed = 0

            for idx, user in enumerate(unique_users, 1):
                try:
                    self.google_service.add_group_member(
                        group_email=group_email,
                        member_email=user['email']
                    )
                    synced += 1
                    job.successful_users += 1
                    job.processed_users += 1

                    # Rate limiting
                    time.sleep(self.API_CALL_DELAY)

                except Exception as e:
                    failed += 1
                    job.failed_users += 1
                    job.processed_users += 1
                    print(f"[GroupSyncProcessor] Failed to add {user['email']}: {str(e)}")

                # Update progress periodically
                if idx % 10 == 0 or idx == total_users:
                    job.progress_percentage = (idx / total_users) * 100
                    self.db.commit()

            # Mark job as completed
            job.created_groups = json.dumps([group_email])
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.progress_percentage = 100.0

            # Update config if this was a first sync
            if config_uuid and config:
                sync_stats = {
                    'added': synced,
                    'removed': 0,
                    'unchanged': 0,
                    'add_failed': failed,
                    'remove_failed': 0,
                    'timestamp': datetime.utcnow().isoformat()
                }
                config.last_sync_stats = json.dumps(sync_stats)
                config.last_synced_at = datetime.utcnow()
                config.last_sync_job_uuid = job_uuid
                config.is_first_sync = False
                config.total_syncs += 1

            self.db.commit()

            print(f"[GroupSyncProcessor] Job completed: {synced} members added, {failed} failed")
            return {
                'status': 'completed',
                'total_users': total_users,
                'successful_users': synced,
                'failed_users': failed,
                'created_groups': [group_email]
            }

        except Exception as e:
            print(f"[GroupSyncProcessor] FATAL ERROR: {str(e)}")
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    def smart_sync(self, config_uuid: str, job_uuid: str) -> Dict:
        """
        Perform a smart sync with delta comparison
        - Get current group members
        - Get expected members from OUs
        - Calculate: to_add, to_remove
        - Apply changes

        Args:
            config_uuid: The configuration UUID
            job_uuid: The job UUID for tracking progress

        Returns:
            Dict with sync results
        """
        print(f"[GroupSyncProcessor] Starting smart_sync for config {config_uuid}")

        # Get config and job
        config = self.db.query(GroupSyncConfig).filter(
            GroupSyncConfig.config_uuid == config_uuid
        ).first()

        if not config:
            raise Exception(f"Config {config_uuid} not found")

        job = self.db.query(BatchJob).filter(
            BatchJob.job_uuid == job_uuid
        ).first()

        if not job:
            raise Exception(f"Job {job_uuid} not found")

        try:
            # Mark job as running
            job.status = 'running'
            job.started_at = datetime.utcnow()
            self.db.commit()

            # Parse config data
            ou_paths = json.loads(config.ou_paths) if config.ou_paths else []
            group_email = config.group_email

            # Step 1: Ensure group exists
            existing_group = self.google_service.get_group(group_email)
            if not existing_group:
                print(f"[GroupSyncProcessor] Group doesn't exist, creating: {group_email}")
                self.google_service.create_group(
                    group_email=group_email,
                    group_name=config.group_name,
                    description=config.group_description or ""
                )
                time.sleep(self.API_CALL_DELAY)

            # Step 2: Get current group members
            print(f"[GroupSyncProcessor] Getting current group members...")
            current_members = set(self.google_service.get_group_members(group_email))
            print(f"[GroupSyncProcessor] Current members: {len(current_members)}")

            # Step 3: Get expected members from OUs
            print(f"[GroupSyncProcessor] Getting expected members from {len(ou_paths)} OUs...")
            expected_members = set()
            for idx, ou_path in enumerate(ou_paths, 1):
                print(f"[GroupSyncProcessor] Getting users from OU {idx}/{len(ou_paths)}: {ou_path}")
                try:
                    users = self.google_service.get_users_in_ou(ou_path)
                    for user in users:
                        expected_members.add(user['email'])
                    print(f"[GroupSyncProcessor] Found {len(users)} users in {ou_path}")
                except Exception as e:
                    print(f"[GroupSyncProcessor] Failed to get users from {ou_path}: {str(e)}")

            print(f"[GroupSyncProcessor] Expected members: {len(expected_members)}")

            # Step 4: Calculate delta
            to_add = expected_members - current_members
            to_remove = current_members - expected_members
            unchanged = current_members & expected_members

            print(f"[GroupSyncProcessor] Delta: +{len(to_add)} -{len(to_remove)} ={len(unchanged)}")

            total_operations = len(to_add) + len(to_remove)
            job.total_users = total_operations
            self.db.commit()

            # Step 5: Add new members
            added = 0
            add_failed = 0

            for idx, member_email in enumerate(to_add, 1):
                try:
                    self.google_service.add_group_member(
                        group_email=group_email,
                        member_email=member_email
                    )
                    added += 1
                    job.successful_users += 1
                    job.processed_users += 1
                    time.sleep(self.API_CALL_DELAY)
                except Exception as e:
                    add_failed += 1
                    job.failed_users += 1
                    job.processed_users += 1
                    print(f"[GroupSyncProcessor] Failed to add {member_email}: {str(e)}")

                # Update progress
                if idx % 10 == 0 or idx == len(to_add):
                    progress = (job.processed_users / total_operations) * 100 if total_operations > 0 else 0
                    job.progress_percentage = progress
                    self.db.commit()

            # Step 6: Remove members no longer in OUs
            removed = 0
            remove_failed = 0

            for idx, member_email in enumerate(to_remove, 1):
                try:
                    self.google_service.remove_group_member(
                        group_email=group_email,
                        member_email=member_email
                    )
                    removed += 1
                    job.successful_users += 1
                    job.processed_users += 1
                    time.sleep(self.API_CALL_DELAY)
                except Exception as e:
                    remove_failed += 1
                    job.failed_users += 1
                    job.processed_users += 1
                    print(f"[GroupSyncProcessor] Failed to remove {member_email}: {str(e)}")

                # Update progress
                progress = (job.processed_users / total_operations) * 100 if total_operations > 0 else 0
                job.progress_percentage = progress
                self.db.commit()

            # Step 7: Update config and job with results
            sync_stats = {
                'added': added,
                'removed': removed,
                'unchanged': len(unchanged),
                'add_failed': add_failed,
                'remove_failed': remove_failed,
                'timestamp': datetime.utcnow().isoformat()
            }

            config.last_sync_stats = json.dumps(sync_stats)
            config.last_synced_at = datetime.utcnow()
            config.last_sync_job_uuid = job_uuid
            config.is_first_sync = False
            config.total_syncs += 1

            job.created_groups = json.dumps([group_email])
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.progress_percentage = 100.0
            self.db.commit()

            print(f"[GroupSyncProcessor] Smart sync completed: +{added} -{removed} ={len(unchanged)}")
            return {
                'status': 'completed',
                'total_users': total_operations,
                'successful_users': added + removed,
                'failed_users': add_failed + remove_failed,
                'created_groups': [group_email],
                'sync_stats': sync_stats
            }

        except Exception as e:
            print(f"[GroupSyncProcessor] FATAL ERROR in smart_sync: {str(e)}")
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    def get_all_configs(self) -> List[Dict]:
        """
        Get all saved group sync configurations

        Returns:
            List of config dictionaries
        """
        configs = self.db.query(GroupSyncConfig).order_by(
            GroupSyncConfig.updated_at.desc()
        ).all()

        result = []
        for config in configs:
            result.append({
                'config_uuid': config.config_uuid,
                'group_email': config.group_email,
                'group_name': config.group_name,
                'group_description': config.group_description,
                'ou_paths': json.loads(config.ou_paths) if config.ou_paths else [],
                'domain': config.domain,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None,
                'last_synced_at': config.last_synced_at.isoformat() if config.last_synced_at else None,
                'last_sync_job_uuid': config.last_sync_job_uuid
            })

        return result

    def delete_config(self, config_uuid: str) -> bool:
        """
        Delete a saved configuration

        Args:
            config_uuid: The configuration UUID to delete

        Returns:
            True if deleted, False if not found
        """
        config = self.db.query(GroupSyncConfig).filter(
            GroupSyncConfig.config_uuid == config_uuid
        ).first()

        if not config:
            return False

        self.db.delete(config)
        self.db.commit()
        return True

    def export_config(self, config_uuid: str) -> Dict:
        """
        Export a single configuration to JSON format

        Args:
            config_uuid: The configuration UUID to export

        Returns:
            Dict with configuration data
        """
        config = self.db.query(GroupSyncConfig).filter(
            GroupSyncConfig.config_uuid == config_uuid
        ).first()

        if not config:
            raise Exception(f"Config {config_uuid} not found")

        return {
            'version': '1.0',
            'export_date': datetime.utcnow().isoformat(),
            'configs': [{
                'group_email': config.group_email,
                'group_name': config.group_name,
                'group_description': config.group_description,
                'ou_paths': json.loads(config.ou_paths) if config.ou_paths else [],
                'domain': config.domain
            }]
        }

    def export_all_configs(self) -> Dict:
        """
        Export all configurations to JSON format

        Returns:
            Dict with all configuration data
        """
        configs = self.db.query(GroupSyncConfig).all()

        exported_configs = []
        for config in configs:
            exported_configs.append({
                'group_email': config.group_email,
                'group_name': config.group_name,
                'group_description': config.group_description,
                'ou_paths': json.loads(config.ou_paths) if config.ou_paths else [],
                'domain': config.domain
            })

        return {
            'version': '1.0',
            'export_date': datetime.utcnow().isoformat(),
            'total_configs': len(exported_configs),
            'configs': exported_configs
        }

    def import_configs(self, import_data: Dict) -> Dict:
        """
        Import configurations from JSON format

        Args:
            import_data: Dict with configuration data

        Returns:
            Dict with import results
        """
        print(f"[GroupSyncProcessor] Starting config import...")

        # Validate format
        if 'version' not in import_data or 'configs' not in import_data:
            raise Exception("Invalid import format: missing 'version' or 'configs' fields")

        if import_data['version'] != '1.0':
            raise Exception(f"Unsupported version: {import_data['version']}")

        configs_to_import = import_data['configs']
        if not isinstance(configs_to_import, list):
            raise Exception("Invalid import format: 'configs' must be a list")

        imported = 0
        skipped = 0
        errors = []

        for idx, config_data in enumerate(configs_to_import, 1):
            try:
                # Validate required fields
                required_fields = ['group_email', 'group_name', 'ou_paths', 'domain']
                missing_fields = [f for f in required_fields if f not in config_data]
                if missing_fields:
                    raise Exception(f"Missing required fields: {', '.join(missing_fields)}")

                # Check if config already exists (by group_email)
                existing = self.db.query(GroupSyncConfig).filter(
                    GroupSyncConfig.group_email == config_data['group_email']
                ).first()

                if existing:
                    print(f"[GroupSyncProcessor] Config already exists: {config_data['group_email']} - skipping")
                    skipped += 1
                    continue

                # Create new config
                new_config = self.create_or_update_config(
                    ou_paths=config_data['ou_paths'],
                    group_email=config_data['group_email'],
                    group_name=config_data['group_name'],
                    group_description=config_data.get('group_description', ''),
                    domain=config_data['domain']
                )

                # Mark as imported
                new_config.imported_from_file = True
                new_config.import_date = datetime.utcnow()
                self.db.commit()

                imported += 1
                print(f"[GroupSyncProcessor] Imported config {idx}/{len(configs_to_import)}: {config_data['group_email']}")

            except Exception as e:
                error_msg = f"Config {idx}: {str(e)}"
                errors.append(error_msg)
                print(f"[GroupSyncProcessor] Failed to import config {idx}: {str(e)}")

        print(f"[GroupSyncProcessor] Import complete: {imported} imported, {skipped} skipped, {len(errors)} errors")

        return {
            'imported': imported,
            'skipped': skipped,
            'failed': len(errors),
            'errors': errors[:10]  # Limit to first 10 errors
        }

    def get_job_status(self, job_uuid: str) -> Dict:
        """
        Get detailed status of a group sync job

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

        # Calculate user status counts
        # Group sync doesn't use cached_users table, so we derive from job counters
        pending = max(0, job.total_users - job.processed_users)
        processing = 0  # Group sync processes synchronously
        success = job.successful_users
        failed = job.failed_users

        user_status_counts = {
            'total': job.total_users,
            'pending': pending,
            'processing': processing,
            'success': success,
            'failed': failed
        }

        return {
            'job_uuid': job.job_uuid,
            'job_type': job.job_type,
            'status': job.status,
            'ou_paths': json.loads(job.ou_paths) if job.ou_paths else [],
            'group_email': job.group_name_pattern,  # Stored in this field
            'group_description': job.group_description,
            'created_groups': json.loads(job.created_groups) if job.created_groups else [],
            'total_users': job.total_users,
            'processed_users': job.processed_users,
            'successful_users': job.successful_users,
            'failed_users': job.failed_users,
            'progress_percentage': job.progress_percentage,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message,
            'user_status_counts': user_status_counts
        }
