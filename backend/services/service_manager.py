"""
Service Manager to ensure Google Workspace service is always available
Automatically recreates service if it becomes None
"""
import os
import json
from typing import Optional
from services.google_workspace import GoogleWorkspaceService
from services.credential_service import CredentialService
from database.session import SessionLocal


class ServiceManager:
    """Manages Google Workspace service lifecycle with auto-recovery"""

    _instance: Optional[GoogleWorkspaceService] = None
    _credentials_path: str = None
    _token_path: str = None
    _delegated_email: str = None
    _credential_type: str = None

    @classmethod
    def initialize(cls, google_service: GoogleWorkspaceService):
        """Initialize the service manager with an existing service"""
        cls._instance = google_service
        if google_service:
            cls._credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
            cls._token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")

    @classmethod
    def get_service(cls) -> GoogleWorkspaceService:
        """
        Get the Google Workspace service, recreating it if necessary

        Returns:
            GoogleWorkspaceService instance

        Raises:
            Exception: If service cannot be created or restored
        """
        # If service exists and is authenticated, return it
        if cls._instance and cls._instance.is_authenticated():
            return cls._instance

        print("[ServiceManager] Service is None or not authenticated, attempting to restore...")

        # Try to restore from database
        try:
            db = SessionLocal()
            cred_service = CredentialService(db)
            active_cred = cred_service.get_active_credential()

            if not active_cred:
                db.close()
                raise Exception("No active credentials found in database")

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

            # Create new service instance
            cls._instance = GoogleWorkspaceService(
                credentials_path,
                token_path,
                active_cred.delegated_email
            )

            # For service accounts, explicitly authenticate
            if active_cred.credential_type == 'service_account' and active_cred.delegated_email:
                cls._instance.authenticate_service_account(active_cred.delegated_email)
                print(f"[ServiceManager] Service account restored and authenticated as {active_cred.delegated_email}")
            else:
                print(f"[ServiceManager] OAuth service restored")

            cls._credentials_path = credentials_path
            cls._token_path = token_path
            cls._delegated_email = active_cred.delegated_email
            cls._credential_type = active_cred.credential_type

            db.close()
            return cls._instance

        except Exception as e:
            print(f"[ServiceManager] Failed to restore service: {str(e)}")
            raise Exception(f"Could not restore authentication: {str(e)}")

    @classmethod
    def is_available(cls) -> bool:
        """Check if service is available and authenticated"""
        try:
            service = cls.get_service()
            return service is not None and service.is_authenticated()
        except:
            return False

    @classmethod
    def clear(cls):
        """Clear the service instance (for logout)"""
        cls._instance = None
        cls._credentials_path = None
        cls._token_path = None
        cls._delegated_email = None
        cls._credential_type = None
