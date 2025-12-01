"""Encryption utilities for securing sensitive data"""
import os
import base64
from cryptography.fernet import Fernet

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    # Generate a default key (should be set in production!)
    print("⚠️  WARNING: Using default encryption key. Set ENCRYPTION_KEY in .env for production!")
    # Create a proper 32-byte key from a fixed seed
    key_material = b'DEA_TOOLBOX_DEFAULT_KEY_CHANGE_ME_IN_PROD_!!!!!'[:32]
    # Pad to 32 bytes if needed
    key_material = key_material.ljust(32, b'0')
    ENCRYPTION_KEY = base64.urlsafe_b64encode(key_material)
else:
    # Convert string key to proper format
    key_material = ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
    ENCRYPTION_KEY = base64.urlsafe_b64encode(key_material)

# Create Fernet cipher
cipher = Fernet(ENCRYPTION_KEY)


def encrypt_data(data: str) -> str:
    """Encrypt string data and return base64 encoded result"""
    encrypted = cipher.encrypt(data.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt base64 encoded data and return original string"""
    encrypted_bytes = base64.b64decode(encrypted_data.encode())
    decrypted = cipher.decrypt(encrypted_bytes)
    return decrypted.decode()
