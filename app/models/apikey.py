import secrets
from typing import Optional, cast

from app.db import db
from app.logger import logger


class ApiKey(db.Model):  # type: ignore
    __tablename__ = "api_keys"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(512), nullable=False, unique=True)
    nightline_id = db.Column(db.Integer, db.ForeignKey("nightlines.id"), nullable=False)
    nightline = db.relationship("Nightline", backref="api_key", foreign_keys=[nightline_id])

    @staticmethod
    def generate_api_key(length: int = 256) -> str:
        """Generate a random API key"""
        logger.debug(f"Generating api key of length: '{length}'")
        return secrets.token_urlsafe(length)

    @classmethod
    def get_api_key(cls, id: int) -> Optional["ApiKey"]:
        """Fetch the API key for nightline"""
        logger.debug(f"Fetching api key for nightline with ID: '{id}'")
        api_key = cast(Optional[ApiKey], cls.query.filter_by(nightline_id=id).first())
        if api_key:
            logger.debug(f"Found api key for nightline with ID: {id}")
        else:
            logger.info(f"Api key for nightline with ID: {id} not found")
        return api_key

    def __repr__(self) -> str:
        return f"ApiKey('{self.id}')"
