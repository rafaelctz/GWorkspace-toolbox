"""Encryption utilities for securing sensitive data"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    # Generate a key from a default password (should be set in production!)
    print("⚠️  WARNING: Using default encryption key. Set ENCRYPTION_KEY in .env for production!")
    ENCRYPTION_KEY = base64.urlsafe_b64encode(b'DEA_TOOLBOX_DEFAULT_KEY_CHANGE_ME_IN_PROD_!!!!!')[:32]
else:
    # Ensure key is proper length
    ENCRYPTION_KEY = base64.urlsafe_b64encode(ENCRYPTION_KEY.encode())[:32]

# Create Fernet cipher
cipher = Fernet(base64.urlsafe_b64encode(ENCRYPTION_KEY + b'=' * (44 - len(ENCRYPTION_KEY))))


def encrypt_data(data: str) -> str:
    """Encrypt string data and return base64 encoded result"""
    encrypted = cipher.encrypt(data.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt base64 encoded data and return original string"""
    encrypted_bytes = base64.b64decode(encrypted_data.encode())
    decrypted = cipher.decrypt(encrypted_bytes)
    return decrypted.decode()
