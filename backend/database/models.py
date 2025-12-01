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
    """Tracks attribute injection jobs"""
    __tablename__ = 'batch_jobs'

    id = Column(Integer, primary_key=True)
    job_uuid = Column(String(36), unique=True, nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # 'attribute_injection'
    status = Column(String(20), nullable=False, index=True)  # 'pending', 'running', 'completed', 'failed'
    ou_paths = Column(Text, nullable=False)  # JSON array of OU paths
    attribute = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
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
