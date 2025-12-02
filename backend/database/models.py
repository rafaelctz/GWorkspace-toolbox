"""SQLAlchemy models for DEA Toolbox"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Credential(Base):
    """Stores encrypted Google Workspace credentials"""
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True)
    credential_type = Column(String(50), nullable=False)  # 'oauth' or 'service_account'
    credentials_data = Column(Text, nullable=False)  # Encrypted JSON
    token_data = Column(Text, nullable=True)  # OAuth token (encrypted)
    delegated_email = Column(String(255), nullable=True)  # For service accounts
    domain = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class BatchJob(Base):
    """Tracks batch jobs (attribute injection, alias extraction, group sync, etc.)"""
    __tablename__ = 'batch_jobs'

    id = Column(Integer, primary_key=True)
    job_uuid = Column(String(36), unique=True, nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # 'attribute_injection', 'alias_extraction', 'group_sync'
    status = Column(String(20), nullable=False, index=True)  # 'pending', 'running', 'completed', 'failed'
    ou_paths = Column(Text, nullable=True)  # JSON array of OU paths
    attribute = Column(String(100), nullable=True)  # For attribute injection
    value = Column(Text, nullable=True)  # For attribute injection
    file_path = Column(Text, nullable=True)  # For alias extraction
    group_name_pattern = Column(String(255), nullable=True)  # For group sync - naming pattern
    group_description = Column(Text, nullable=True)  # For group sync - description template
    created_groups = Column(Text, nullable=True)  # For group sync - JSON array of created group emails
    total_users = Column(Integer, default=0)
    processed_users = Column(Integer, default=0)
    successful_users = Column(Integer, default=0)
    failed_users = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)


class CachedUser(Base):
    """Stores users from selected OUs for processing"""
    __tablename__ = 'cached_users'

    id = Column(Integer, primary_key=True)
    job_uuid = Column(String(36), ForeignKey('batch_jobs.job_uuid'), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    ou_path = Column(String(500), nullable=False)
    user_data = Column(Text, nullable=True)  # JSON with full user profile
    status = Column(String(20), default='pending', index=True)  # 'pending', 'processing', 'success', 'failed'
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)


class BatchOperation(Base):
    """Tracks individual batch executions within a job"""
    __tablename__ = 'batch_operations'

    id = Column(Integer, primary_key=True)
    job_uuid = Column(String(36), ForeignKey('batch_jobs.job_uuid'), nullable=False, index=True)
    batch_number = Column(Integer, nullable=False)
    user_emails = Column(Text, nullable=False)  # JSON array of emails in this batch
    status = Column(String(20), nullable=False)  # 'pending', 'running', 'completed', 'failed'
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class GroupSyncConfig(Base):
    """Saved configurations for OU to Group syncing - reusable sync mappings"""
    __tablename__ = 'group_sync_configs'

    id = Column(Integer, primary_key=True)
    config_uuid = Column(String(36), unique=True, nullable=False, index=True)
    group_email = Column(String(255), nullable=False)
    group_name = Column(String(255), nullable=False)
    group_description = Column(Text, nullable=True)
    ou_paths = Column(Text, nullable=False)  # JSON array of OU paths
    domain = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=True)
    last_sync_job_uuid = Column(String(36), nullable=True)  # Reference to most recent sync job

    # Smart Sync fields
    is_first_sync = Column(Boolean, default=True)  # Track if this config has been synced before
    last_sync_stats = Column(Text, nullable=True)  # JSON with last sync statistics (added, removed, unchanged)
    total_syncs = Column(Integer, default=0)  # Counter for total number of syncs performed
    imported_from_file = Column(Boolean, default=False)  # Track if config was imported vs created manually
    import_date = Column(DateTime, nullable=True)  # When the config was imported


class GroupSyncOperation(Base):
    """Tracks individual OU to Group sync operations"""
    __tablename__ = 'group_sync_operations'

    id = Column(Integer, primary_key=True)
    job_uuid = Column(String(36), ForeignKey('batch_jobs.job_uuid'), nullable=False, index=True)
    ou_path = Column(String(500), nullable=False)
    ou_name = Column(String(255), nullable=False)
    group_email = Column(String(255), nullable=False)
    group_name = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False)  # 'pending', 'creating_group', 'syncing_members', 'completed', 'failed'
    total_members = Column(Integer, default=0)
    synced_members = Column(Integer, default=0)
    failed_members = Column(Integer, default=0)
    group_created = Column(Boolean, default=False)  # Whether group was newly created or already existed
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
