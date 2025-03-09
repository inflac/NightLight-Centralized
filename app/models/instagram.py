import os
import base64

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

from app.db import db
from app.config import Config

class InstagramAccount(db.Model):
    __tablename__ = "instagram_accounts"
    id = db.Column(db.Integer, primary_key=True)
    nightline_id = db.Column(
        db.Integer,
        db.ForeignKey("nightlines.id"),
        unique=True,
        nullable=False)
    nightline = db.relationship(
        "Nightline",
        uselist=False,
        single_parent=True,
        back_populates="instagram_account")
    username = db.Column(db.String(50), nullable=False)
    encrypted_password = db.Column(db.String(100), nullable=False)
    salt = db.Column(db.String(255), nullable=False)
    session_data = db.Column(db.Text, nullable=True)

    def derive_key(self):
        """Derives an encryption key using PBKDF2 with the stored salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key for AES
            salt=base64.urlsafe_b64decode(self.salt),
            iterations=100_000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(
            kdf.derive(Config.ENCRYPTION_PASSWORD.encode()))
        return Fernet(key)

    def set_username(self, username: str):
        """Set the username of an account."""
        self.username = username
        db.session.commit()

    def set_password(self, password: str):
        """Securely store the password of an account."""
        self.salt = base64.urlsafe_b64encode(
            os.urandom(16)).decode()  # Generate a 16-byte salt
        cipher = self.derive_key()
        self.encrypted_password = cipher.encrypt(password.encode()).decode()
        db.session.commit()

    def get_password(self):
        """Decrypts and returns the stored password."""
        cipher = self.derive_key()
        return cipher.decrypt(self.encrypted_password.encode()).decode()
