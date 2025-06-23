import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy.exc import SQLAlchemyError

from app.config import Config
from app.db import db
from app.logger import logger


class InstagramAccount(db.Model):  # type: ignore
    __tablename__ = "instagram_accounts"
    id = db.Column(db.Integer, primary_key=True)
    nightline_id = db.Column(db.Integer, db.ForeignKey("nightlines.id"), unique=True, nullable=False)
    nightline = db.relationship(
        "Nightline",
        uselist=False,
        single_parent=True,
        back_populates="instagram_account",
    )
    username = db.Column(db.String(50), nullable=False)
    encrypted_password = db.Column(db.String(100), nullable=False)
    salt = db.Column(db.String(255), nullable=False)
    session_data = db.Column(db.Text, nullable=True)

    def derive_key(self) -> Fernet:
        """Derives an encryption key using PBKDF2 with the stored salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key for AES
            salt=base64.urlsafe_b64decode(self.salt),
            iterations=100_000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(Config.ENCRYPTION_PASSWORD.encode()))
        return Fernet(key)

    def set_username(self, username: str) -> bool:
        """Set the username of an account. Returns True if successful, False otherwise."""
        self.username = username
        try:
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Failed to set username for user_id={self.id}: {e}")
            return False

    def set_password(self, password: str) -> bool:
        """Securely store the password of an account."""
        try:
            self.salt = base64.urlsafe_b64encode(os.urandom(16)).decode()  # Generate a 16-byte salt
            cipher = self.derive_key()
            self.encrypted_password = cipher.encrypt(password.encode()).decode()
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error when setting password for user_id={self.id}: {e}")
            return False
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Unexpected error when setting password for user_id={self.id}: {e}")
            return False

    def get_password(self) -> Optional[str]:
        """Decrypts and returns the stored password. Returns None if decryption fails."""
        try:
            cipher = self.derive_key()
            return cipher.decrypt(self.encrypted_password.encode()).decode()
        except Exception:
            logger.exception(f"Failed to decrypt password for user_id={self.id}")
            return None
