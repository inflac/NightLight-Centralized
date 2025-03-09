import os
import base64
from app.db import db
from config import Config
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

class InstagramAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nightline_id = db.Column(db.Integer, db.ForeignKey("nightline.id"), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    encrypted_password = db.Column(db.String(255), nullable=False)  # Encrypted password
    salt = db.Column(db.String(255), nullable=False)  # Unique salt per account
    session_data = db.Column(db.Text, nullable=True)  # Stores Instagram session data

    def derive_key(self):
        """Derives an encryption key using PBKDF2 with the stored salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key for AES
            salt=base64.urlsafe_b64decode(self.salt),
            iterations=100_000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(Config.ENCRYPTION_PASSWORD.encode()))
        return Fernet(key)

    def set_password(self, password):
        """Generates a random salt and encrypts the password."""
        self.salt = base64.urlsafe_b64encode(os.urandom(16)).decode()  # Generate a 16-byte salt
        cipher = self.derive_key()
        self.encrypted_password = cipher.encrypt(password.encode()).decode()

    def get_password(self):
        """Decrypts and returns the stored password."""
        cipher = self.derive_key()
        return cipher.decrypt(self.encrypted_password.encode()).decode()
