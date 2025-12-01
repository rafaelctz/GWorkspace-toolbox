"""Service for managing Google Workspace credentials in database"""
import json
from typing import Optional, Dict
from sqlalchemy.orm import Session
from database.models import Credential
from utils.encryption import encrypt_data, decrypt_data


class CredentialService:
    """Handles credential storage and retrieval from database"""

    def __init__(self, db: Session):
        self.db = db

    def save_credentials(
        self,
        credentials_data: Dict,
        credential_type: str,
        token_data: Optional[Dict] = None,
        delegated_email: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Credential:
        """
        Save or update credentials in database

        Args:
            credentials_data: The Google credentials JSON
            credential_type: 'oauth' or 'service_account'
            token_data: OAuth token data (optional)
            delegated_email: For service accounts with delegation
            domain: Google Workspace domain

        Returns:
            Credential: The saved credential record
        """
        # Deactivate all existing credentials
        self.db.query(Credential).update({"is_active": False})

        # Encrypt the credentials
        encrypted_creds = encrypt_data(json.dumps(credentials_data))
        encrypted_token = encrypt_data(json.dumps(token_data)) if token_data else None

        # Create new credential
        credential = Credential(
            credential_type=credential_type,
            credentials_data=encrypted_creds,
            token_data=encrypted_token,
            delegated_email=delegated_email,
            domain=domain,
            is_active=True
        )

        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)

        return credential

    def get_active_credential(self) -> Optional[Credential]:
        """Get the currently active credential"""
        return self.db.query(Credential).filter(
            Credential.is_active == True
        ).first()

    def get_credentials_data(self, credential: Credential) -> Dict:
        """Decrypt and return credentials JSON"""
        decrypted = decrypt_data(credential.credentials_data)
        return json.loads(decrypted)

    def get_token_data(self, credential: Credential) -> Optional[Dict]:
        """Decrypt and return token JSON"""
        if not credential.token_data:
            return None
        decrypted = decrypt_data(credential.token_data)
        return json.loads(decrypted)

    def update_token(self, credential_id: int, token_data: Dict) -> None:
        """Update OAuth token for a credential"""
        credential = self.db.query(Credential).filter(
            Credential.id == credential_id
        ).first()

        if credential:
            credential.token_data = encrypt_data(json.dumps(token_data))
            self.db.commit()

    def delete_all_credentials(self) -> None:
        """Delete all credentials from database"""
        self.db.query(Credential).delete()
        self.db.commit()

    def has_credentials(self) -> bool:
        """Check if any credentials exist in database"""
        return self.db.query(Credential).filter(
            Credential.is_active == True
        ).count() > 0
