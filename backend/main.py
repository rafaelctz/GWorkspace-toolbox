from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime

from services.google_workspace import GoogleWorkspaceService
from services.credential_service import CredentialService
from services.batch_processor import BatchProcessor
from services.group_sync_processor import GroupSyncProcessor
from services.service_manager import ServiceManager
from database.session import init_db, get_db

load_dotenv()

app = FastAPI(
    title="DEA Toolbox API",
    description="Tools for AD administrators to manage SAML and SSO integrations",
    version="2.0.0"  # Updated for database version
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables and restore credentials from database"""
    global google_service

    init_db()
    print("✓ Database initialized")

    # Try to restore credentials from database
    try:
        from database.session import SessionLocal
        db = SessionLocal()
        cred_service = CredentialService(db)

        active_cred = cred_service.get_active_credential()
        if active_cred:
            # Restore credentials to files
            credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
            token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")

            # Write credentials file
            creds_data = cred_service.get_credentials_data(active_cred)
            with open(credentials_path, 'w') as f:
                json.dump(creds_data, f)

            # Write token file if exists (for OAuth)
            token_data = cred_service.get_token_data(active_cred)
            if token_data:
                with open(token_path, 'w') as f:
                    json.dump(token_data, f)

            # Initialize service
            google_service = GoogleWorkspaceService(
                credentials_path,
                token_path,
                active_cred.delegated_email
            )

            # For service accounts, explicitly authenticate with delegated email
            if active_cred.credential_type == 'service_account' and active_cred.delegated_email:
                try:
                    google_service.authenticate_service_account(active_cred.delegated_email)
                    print(f"✓ Service account auto-authenticated as {active_cred.delegated_email}")
                except Exception as e:
                    print(f"⚠️  Service account authentication failed: {str(e)}")
                    google_service = None

            # Initialize ServiceManager with the service
            ServiceManager.initialize(google_service)
            print(f"✓ ServiceManager initialized")

            print(f"✓ Credentials restored from database ({active_cred.credential_type})")
            if google_service and google_service.is_authenticated():
                user_email = active_cred.delegated_email if active_cred.credential_type == 'service_account' else 'OAuth user'
                print(f"✓ Auto-authenticated as {user_email}")

        db.close()
    except Exception as e:
        print(f"⚠️  Could not restore credentials: {str(e)}")

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
google_service: Optional[GoogleWorkspaceService] = None


class StatusResponse(BaseModel):
    authenticated: bool
    admin_email: Optional[str] = None
    domain: Optional[str] = None


class AliasExtractionResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    total_users: Optional[int] = None
    users_with_aliases: Optional[int] = None


@app.get("/")
async def root():
    return {
        "message": "GWorkspace Toolbox API",
        "version": "2.0.0",
        "status": "running",
        "features": ["alias_extractor", "attribute_injector", "batch_processing", "database"]
    }


@app.get("/api/health/database")
async def database_health(db: Session = Depends(get_db)):
    """Check database connection health"""
    try:
        from sqlalchemy import text
        # Simple query to verify database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "type": "sqlite"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Check if Google Workspace API is authenticated"""
    try:
        # Use ServiceManager to get service (auto-recovers if None)
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            return StatusResponse(authenticated=False)

        info = google_service.get_admin_info()
        return StatusResponse(
            authenticated=True,
            admin_email=info.get("email"),
            domain=info.get("domain")
        )
    except Exception as e:
        return StatusResponse(authenticated=False)


@app.post("/api/auth/upload-credentials")
async def upload_credentials(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload Google OAuth or Service Account credentials JSON file"""
    try:
        contents = await file.read()
        credentials_data = json.loads(contents)

        # Validate credentials structure - accept both OAuth and Service Account
        is_oauth = "installed" in credentials_data or "web" in credentials_data
        is_service_account = "type" in credentials_data and credentials_data["type"] == "service_account"

        if not is_oauth and not is_service_account:
            raise HTTPException(
                status_code=400,
                detail="Invalid credentials format. Please upload either an OAuth 2.0 Client ID credential (Desktop app) or a Service Account credential from Google Cloud Console."
            )

        # Determine credential type
        credential_type = "service_account" if is_service_account else "oauth"

        # Save to database
        cred_service = CredentialService(db)
        cred_service.save_credentials(
            credentials_data=credentials_data,
            credential_type=credential_type
        )

        # Also save to file for immediate use
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        with open(credentials_path, "w") as f:
            json.dump(credentials_data, f)

        return {
            "message": "Credentials uploaded and saved successfully",
            "credential_type": credential_type
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON file. Please ensure the file is a valid JSON format downloaded from Google Cloud Console."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading credentials: {str(e)}")


@app.post("/api/auth/authenticate")
async def authenticate(db: Session = Depends(get_db)):
    """Start OAuth flow and authenticate with Google Workspace"""
    global google_service

    try:
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")

        if not os.path.exists(credentials_path):
            raise HTTPException(
                status_code=400,
                detail="Credentials file not found. Please upload credentials first."
            )

        google_service = GoogleWorkspaceService(credentials_path, token_path)
        google_service.authenticate()

        info = google_service.get_admin_info()

        # Save token to database
        if os.path.exists(token_path):
            with open(token_path, 'r') as f:
                token_data = json.load(f)

            cred_service = CredentialService(db)
            active_cred = cred_service.get_active_credential()
            if active_cred:
                cred_service.update_token(active_cred.id, token_data)

                # Update domain info
                active_cred.domain = info.get("domain")
                db.commit()

        # Initialize ServiceManager with authenticated service
        ServiceManager.initialize(google_service)

        return {
            "message": "Authentication successful",
            "admin_email": info.get("email"),
            "domain": info.get("domain")
        }

    except FileNotFoundError as e:
        google_service = None
        ServiceManager.clear()
        raise HTTPException(
            status_code=400,
            detail="Credentials file not found. Please upload credentials first."
        )
    except Exception as e:
        # Reset service on failure
        google_service = None
        ServiceManager.clear()

        error_msg = str(e)
        if "invalid_grant" in error_msg.lower():
            error_msg = "Authentication failed. The authorization code or refresh token may be invalid or expired. Please try again."
        elif "access_denied" in error_msg.lower():
            error_msg = "Access denied. You may have cancelled the authorization or don't have sufficient permissions."
        elif "redirect_uri_mismatch" in error_msg.lower():
            error_msg = "OAuth redirect URI mismatch. Please check your Google Cloud Console OAuth configuration."

        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/api/auth/authenticate-service-account")
async def authenticate_service_account(request: dict, db: Session = Depends(get_db)):
    """Authenticate using service account with domain-wide delegation"""
    global google_service

    try:
        delegated_email = request.get("delegated_email")
        if not delegated_email:
            raise HTTPException(
                status_code=400,
                detail="Delegated admin email is required for service account authentication"
            )

        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")

        if not os.path.exists(credentials_path):
            raise HTTPException(
                status_code=400,
                detail="Credentials file not found. Please upload service account credentials first."
            )

        google_service = GoogleWorkspaceService(credentials_path, token_path, delegated_email)
        google_service.authenticate_service_account(delegated_email)

        # Get domain from delegated email
        domain = delegated_email.split('@')[1] if '@' in delegated_email else ''

        # Update database with delegated email and domain
        cred_service = CredentialService(db)
        active_cred = cred_service.get_active_credential()
        if active_cred:
            active_cred.delegated_email = delegated_email
            active_cred.domain = domain
            db.commit()

        # Initialize ServiceManager with authenticated service
        ServiceManager.initialize(google_service)

        return {
            "message": "Service account authentication successful",
            "admin_email": delegated_email,
            "domain": domain,
            "auth_type": "service_account"
        }

    except FileNotFoundError as e:
        google_service = None
        ServiceManager.clear()
        raise HTTPException(
            status_code=400,
            detail="Service account credentials file not found. Please upload credentials first."
        )
    except Exception as e:
        # Reset service on failure
        google_service = None
        ServiceManager.clear()

        error_msg = str(e)
        if "domain-wide delegation" in error_msg.lower() or "delegated" in error_msg.lower():
            error_msg = "Service account authentication failed. Make sure domain-wide delegation is enabled for this service account in your Google Workspace Admin Console."

        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/auth/credential-type")
async def get_credential_type():
    """Detect the type of uploaded credentials"""
    try:
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")

        if not os.path.exists(credentials_path):
            return {"type": None, "exists": False}

        with open(credentials_path, 'r') as f:
            import json
            cred_data = json.load(f)

            if 'type' in cred_data and cred_data['type'] == 'service_account':
                return {
                    "type": "service_account",
                    "exists": True,
                    "service_account_email": cred_data.get('client_email', '')
                }
            elif 'installed' in cred_data or 'web' in cred_data:
                return {
                    "type": "oauth",
                    "exists": True
                }
            else:
                return {
                    "type": "unknown",
                    "exists": True
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/logout")
async def logout(db: Session = Depends(get_db)):
    """Logout and clear authentication (keeps credentials, removes token)"""
    global google_service

    try:
        token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")
        if os.path.exists(token_path):
            os.remove(token_path)

        # Clear token from database (keep credentials)
        cred_service = CredentialService(db)
        active_cred = cred_service.get_active_credential()
        if active_cred:
            active_cred.token_data = None
            db.commit()

        google_service = None
        ServiceManager.clear()

        return {"message": "Logged out successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/auth/credentials")
async def delete_credentials(db: Session = Depends(get_db)):
    """Delete uploaded credentials and clear database"""
    global google_service

    try:
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")

        # Remove both files if they exist
        if os.path.exists(credentials_path):
            os.remove(credentials_path)

        if os.path.exists(token_path):
            os.remove(token_path)

        # Delete from database
        cred_service = CredentialService(db)
        cred_service.delete_all_credentials()

        # Reset service
        google_service = None
        ServiceManager.clear()

        return {"message": "Credentials deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/credentials-status")
async def credentials_status(db: Session = Depends(get_db)):
    """Check if credentials exist in database or file"""
    try:
        cred_service = CredentialService(db)
        has_db_creds = cred_service.has_credentials()

        active_cred = cred_service.get_active_credential()

        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        file_exists = os.path.exists(credentials_path)

        return {
            "exists": has_db_creds or file_exists,
            "in_database": has_db_creds,
            "in_file": file_exists,
            "credential_type": active_cred.credential_type if active_cred else None,
            "domain": active_cred.domain if active_cred else None,
            "delegated_email": active_cred.delegated_email if active_cred else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tools/extract-aliases", response_model=AliasExtractionResponse)
async def extract_aliases():
    """Extract all users with aliases from Google Workspace"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(
                status_code=401,
                detail="Not authenticated. Please authenticate first."
            )

        result = google_service.extract_aliases_to_csv()

        return AliasExtractionResponse(
            success=True,
            message="Aliases extracted successfully",
            file_path=result["file_path"],
            total_users=result["total_users"],
            users_with_aliases=result["users_with_aliases"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools/download-aliases")
async def download_aliases(file_path: str):
    """Download the generated CSV file"""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="text/csv"
    )


@app.get("/api/tools/organizational-units")
async def get_organizational_units():
    """Get all organizational units from Google Workspace"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        org_units = google_service.get_organizational_units()
        return {"organizational_units": org_units}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tools/inject-attribute")
async def inject_attribute(request: dict):
    """Inject an attribute to users in selected OUs (synchronous - legacy)"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        ou_paths = request.get("ou_paths", [])
        attribute = request.get("attribute")
        value = request.get("value")

        if not ou_paths:
            raise HTTPException(status_code=400, detail="At least one OU path is required")
        if not attribute:
            raise HTTPException(status_code=400, detail="Attribute name is required")
        if value is None or value == "":
            raise HTTPException(status_code=400, detail="Value is required")

        result = google_service.inject_attribute_to_users(ou_paths, attribute, value)
        return {
            "success": True,
            "message": f"Attribute injected successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Batch Processing Endpoints (Async)

@app.post("/api/batch/extract-aliases")
async def batch_extract_aliases(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Create a batch job to extract aliases asynchronously
    Returns immediately with job UUID for status tracking
    """
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Generate unique job ID
        job_uuid = str(uuid.uuid4())

        # Generate file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = f'./exports/google_workspace_aliases_{timestamp}.csv'

        # Create job record
        from database.models import BatchJob
        job = BatchJob(
            job_uuid=job_uuid,
            job_type='alias_extraction',
            status='pending',
            file_path=file_path,
            total_users=0,
            processed_users=0,
            successful_users=0,
            failed_users=0,
            progress_percentage=0.0
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Start background processing
        background_tasks.add_task(_process_alias_extraction_job, job_uuid)

        return {
            "success": True,
            "message": "Alias extraction job created and processing started",
            "job_uuid": job.job_uuid
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/inject-attribute")
async def batch_inject_attribute(request: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Create a batch job to inject attribute asynchronously
    Returns immediately with job UUID for status tracking
    """
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        ou_paths = request.get("ou_paths", [])
        attribute = request.get("attribute")
        value = request.get("value")

        if not ou_paths:
            raise HTTPException(status_code=400, detail="At least one OU path is required")
        if not attribute:
            raise HTTPException(status_code=400, detail="Attribute name is required")
        if value is None or value == "":
            raise HTTPException(status_code=400, detail="Value is required")

        # Create batch processor
        processor = BatchProcessor(db, google_service)

        # Create job and cache users
        job = processor.create_job(
            ou_paths=ou_paths,
            attribute=attribute,
            value=value
        )

        # Start background processing
        background_tasks.add_task(
            _process_batch_job,
            job_uuid=job.job_uuid
        )

        return {
            "success": True,
            "message": "Batch job created and processing started",
            "job_uuid": job.job_uuid,
            "total_users": job.total_users
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/jobs/{job_uuid}")
async def get_batch_job_status(job_uuid: str, db: Session = Depends(get_db)):
    """Get status and progress of a specific batch job"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        processor = BatchProcessor(db, google_service)
        status = processor.get_job_status(job_uuid)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/batch/jobs")
async def list_batch_jobs(limit: int = 50, db: Session = Depends(get_db)):
    """List all batch jobs ordered by creation date"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        processor = BatchProcessor(db, google_service)
        jobs = processor.get_all_jobs(limit=limit)
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/jobs/{job_uuid}/failed-users")
async def get_failed_users(job_uuid: str, db: Session = Depends(get_db)):
    """Get all failed users for a specific job with their error messages"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        processor = BatchProcessor(db, google_service)
        failed_users = processor.get_failed_users(job_uuid)
        return {"failed_users": failed_users, "count": len(failed_users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/jobs/{job_uuid}/restart")
async def restart_batch_job(job_uuid: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Restart a pending or failed batch job
    Returns immediately and processes the job in the background
    """
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Get the job
        from database.models import BatchJob, CachedUser
        job = db.query(BatchJob).filter(BatchJob.job_uuid == job_uuid).first()

        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_uuid} not found")

        # Only restart pending or failed jobs
        if job.status not in ['pending', 'failed']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot restart job with status '{job.status}'. Only 'pending' or 'failed' jobs can be restarted."
            )

        # Reset any users in 'processing' state back to 'pending'
        processing_users = db.query(CachedUser).filter(
            CachedUser.job_uuid == job_uuid,
            CachedUser.status == 'processing'
        ).all()

        for user in processing_users:
            user.status = 'pending'

        # Reset job to pending state if it was failed
        if job.status == 'failed':
            job.status = 'pending'
            job.error_message = None
            job.completed_at = None

        db.commit()

        # Add the job to background tasks
        background_tasks.add_task(_process_batch_job, job_uuid)

        return {
            "message": "Job restart initiated",
            "job_uuid": job_uuid,
            "status": "pending"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/sync-ou-groups")
async def sync_ou_groups(request: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Create a saved configuration and sync job for OU to Group synchronization
    Returns immediately with job UUID and config UUID for status tracking
    """
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        ou_paths = request.get("ou_paths", [])
        group_email = request.get("group_email")
        group_name = request.get("group_name", "")
        group_description = request.get("group_description", "")

        if not ou_paths:
            raise HTTPException(status_code=400, detail="At least one OU path is required")

        if not group_email:
            raise HTTPException(status_code=400, detail="Group email is required")

        # Get domain from admin info
        admin_info = google_service.get_admin_info()
        domain = admin_info.get("domain")
        if not domain:
            raise HTTPException(status_code=400, detail="Could not determine domain from authenticated user")

        # Create group sync processor
        processor = GroupSyncProcessor(db, google_service)

        # Create or update config
        config = processor.create_or_update_config(
            ou_paths=ou_paths,
            group_email=group_email,
            group_name=group_name or group_email.split('@')[0],
            group_description=group_description,
            domain=domain
        )

        # Create job from config
        job = processor.create_sync_job(config.config_uuid)

        # Start background processing
        background_tasks.add_task(
            _process_group_sync_job,
            job_uuid=job.job_uuid
        )

        return {
            "success": True,
            "message": "Group sync configuration saved and job created",
            "job_uuid": job.job_uuid,
            "config_uuid": config.config_uuid,
            "ou_count": len(ou_paths),
            "group_email": group_email
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/group-sync/configs")
async def get_group_sync_configs(db: Session = Depends(get_db)):
    """Get all saved group sync configurations"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        processor = GroupSyncProcessor(db, google_service)
        configs = processor.get_all_configs()

        return {"configs": configs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/group-sync/configs/{config_uuid}/sync")
async def resync_config(config_uuid: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Re-run sync for a saved configuration"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        processor = GroupSyncProcessor(db, google_service)

        # Create job from config
        job = processor.create_sync_job(config_uuid)

        # Start background processing
        background_tasks.add_task(
            _process_group_sync_job,
            job_uuid=job.job_uuid
        )

        return {
            "success": True,
            "message": "Group sync job created from saved configuration",
            "job_uuid": job.job_uuid,
            "config_uuid": config_uuid
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/group-sync/configs/{config_uuid}")
async def delete_config(config_uuid: str, db: Session = Depends(get_db)):
    """Delete a saved group sync configuration"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        processor = GroupSyncProcessor(db, google_service)
        success = processor.delete_config(config_uuid)

        if not success:
            raise HTTPException(status_code=404, detail=f"Configuration {config_uuid} not found")

        return {
            "success": True,
            "message": "Configuration deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/group-sync/configs/export-all")
async def export_all_configs(db: Session = Depends(get_db)):
    """Export all group sync configurations to JSON"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        processor = GroupSyncProcessor(db, google_service)
        export_data = processor.export_all_configs()

        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"group_sync_configs_{timestamp}.json"

        # Return JSON file as download
        return Response(
            content=json.dumps(export_data, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/group-sync/configs/{config_uuid}/export")
async def export_single_config(config_uuid: str, db: Session = Depends(get_db)):
    """Export a single group sync configuration to JSON"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        processor = GroupSyncProcessor(db, google_service)
        export_data = processor.export_config(config_uuid)

        if not export_data:
            raise HTTPException(status_code=404, detail=f"Configuration {config_uuid} not found")

        # Generate filename with config name
        config_name = export_data['configs'][0]['group_email'].replace('@', '_').replace('.', '_')
        filename = f"group_sync_config_{config_name}.json"

        # Return JSON file as download
        return Response(
            content=json.dumps(export_data, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/group-sync/configs/import")
async def import_configs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import group sync configurations from JSON file"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")

        # Read and parse JSON file
        content = await file.read()
        try:
            import_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")

        # Import configurations
        processor = GroupSyncProcessor(db, google_service)
        result = processor.import_configs(import_data)

        return {
            "success": True,
            "message": f"Imported {result['imported']} configurations, skipped {result['skipped']}, failed {result['failed']}",
            "imported": result['imported'],
            "skipped": result['skipped'],
            "failed": result['failed'],
            "details": result.get('details', [])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/group-sync/configs/sync-all")
async def sync_all_configs(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Sync all saved configurations sequentially"""
    try:
        google_service = ServiceManager.get_service()

        if not google_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated")

        processor = GroupSyncProcessor(db, google_service)

        # Get all configs
        configs = processor.get_all_configs()

        if not configs:
            raise HTTPException(status_code=404, detail="No configurations found")

        # Create jobs for all configs
        job_uuids = []
        for config in configs:
            try:
                job = processor.create_sync_job(config['config_uuid'])
                job_uuids.append(job.job_uuid)

                # Start background processing for this job
                background_tasks.add_task(
                    _process_group_sync_job,
                    job_uuid=job.job_uuid
                )
            except Exception as e:
                print(f"[sync_all_configs] Failed to create job for config {config['config_uuid']}: {str(e)}")

        return {
            "success": True,
            "message": f"Created {len(job_uuids)} sync jobs",
            "total_configs": len(configs),
            "jobs_created": len(job_uuids),
            "job_uuids": job_uuids
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _process_batch_job(job_uuid: str):
    """Background task to process a batch job"""
    from database.session import SessionLocal
    import traceback

    print(f"[_process_batch_job] Starting background task for job {job_uuid}")
    db = SessionLocal()
    try:
        # Use ServiceManager to get service (auto-recovers if None)
        print(f"[_process_batch_job] Getting service from ServiceManager...")
        google_service = ServiceManager.get_service()

        if google_service and google_service.is_authenticated():
            print(f"[_process_batch_job] Google service available and authenticated, creating batch processor")
            processor = BatchProcessor(db, google_service)
            print(f"[_process_batch_job] Calling process_job...")
            processor.process_job(job_uuid)
            print(f"[_process_batch_job] process_job completed successfully")
        else:
            print(f"[_process_batch_job] ERROR: Service not authenticated!")
            raise Exception("Google service not available or not authenticated")
    except Exception as e:
        print(f"[_process_batch_job] ❌ EXCEPTION in background task for job {job_uuid}: {str(e)}")
        traceback.print_exc()
    finally:
        print(f"[_process_batch_job] Closing database session for job {job_uuid}")
        db.close()


def _process_alias_extraction_job(job_uuid: str):
    """Background task to process an alias extraction job"""
    from database.session import SessionLocal
    from database.models import BatchJob
    import traceback

    print(f"[_process_alias_extraction_job] Starting alias extraction for job {job_uuid}")
    db = SessionLocal()

    try:
        # Get the job
        job = db.query(BatchJob).filter(BatchJob.job_uuid == job_uuid).first()
        if not job:
            print(f"[_process_alias_extraction_job] ERROR: Job {job_uuid} not found")
            return

        # Update job status to running
        job.status = 'running'
        job.started_at = datetime.now()
        db.commit()

        # Get Google service
        print(f"[_process_alias_extraction_job] Getting service from ServiceManager...")
        google_service = ServiceManager.get_service()

        if not google_service or not google_service.is_authenticated():
            print(f"[_process_alias_extraction_job] ERROR: Service not authenticated!")
            job.status = 'failed'
            job.error_message = "Google service not available or not authenticated"
            job.completed_at = datetime.now()
            db.commit()
            return

        # Progress callback
        def progress_callback(total, processed, users_with_aliases):
            print(f"[_process_alias_extraction_job] Progress: {processed}/{total} users processed, {users_with_aliases} with aliases")
            job.total_users = total
            job.processed_users = processed
            job.successful_users = users_with_aliases
            job.progress_percentage = (processed / total * 100) if total > 0 else 0
            db.commit()

        # Run the extraction
        print(f"[_process_alias_extraction_job] Starting streaming extraction to {job.file_path}")
        result = google_service.extract_aliases_streaming(
            file_path=job.file_path,
            progress_callback=progress_callback
        )

        # Update job with final results
        job.status = 'completed'
        job.total_users = result['total_users']
        job.processed_users = result['total_users']
        job.successful_users = result['users_with_aliases']
        job.progress_percentage = 100.0
        job.completed_at = datetime.now()
        db.commit()

        print(f"[_process_alias_extraction_job] Completed successfully: {result['users_with_aliases']} users with aliases")

    except Exception as e:
        print(f"[_process_alias_extraction_job] ❌ EXCEPTION: {str(e)}")
        traceback.print_exc()

        # Mark job as failed
        try:
            job = db.query(BatchJob).filter(BatchJob.job_uuid == job_uuid).first()
            if job:
                job.status = 'failed'
                job.error_message = str(e)
                job.completed_at = datetime.now()
                db.commit()
        except:
            pass
    finally:
        print(f"[_process_alias_extraction_job] Closing database session for job {job_uuid}")
        db.close()


def _process_group_sync_job(job_uuid: str):
    """Background task to process a group sync job"""
    from database.session import SessionLocal
    import traceback

    print(f"[_process_group_sync_job] Starting group sync for job {job_uuid}")
    db = SessionLocal()

    try:
        # Get Google service
        print(f"[_process_group_sync_job] Getting service from ServiceManager...")
        google_service = ServiceManager.get_service()

        if not google_service or not google_service.is_authenticated():
            print(f"[_process_group_sync_job] ERROR: Service not authenticated!")
            # Mark job as failed
            from database.models import BatchJob
            job = db.query(BatchJob).filter(BatchJob.job_uuid == job_uuid).first()
            if job:
                job.status = 'failed'
                job.error_message = "Google service not available or not authenticated"
                job.completed_at = datetime.now()
                db.commit()
            return

        # Create processor and run the job
        processor = GroupSyncProcessor(db, google_service)
        processor.process_job(job_uuid)

        print(f"[_process_group_sync_job] Completed successfully")

    except Exception as e:
        print(f"[_process_group_sync_job] ❌ EXCEPTION: {str(e)}")
        traceback.print_exc()

        # Mark job as failed
        try:
            from database.models import BatchJob
            job = db.query(BatchJob).filter(BatchJob.job_uuid == job_uuid).first()
            if job:
                job.status = 'failed'
                job.error_message = str(e)
                job.completed_at = datetime.now()
                db.commit()
        except:
            pass
    finally:
        print(f"[_process_group_sync_job] Closing database session for job {job_uuid}")
        db.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
