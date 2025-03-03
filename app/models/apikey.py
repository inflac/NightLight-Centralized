import secrets
from ..db import db

class ApiKey(db.Model):
    __tablename__ = "api_keys"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(512), nullable=False, unique=True)
    nightline_id = db.Column(
        db.Integer,
        db.ForeignKey("nightlines.id"),
        nullable=False)

    nightline = db.relationship("Nightline", back_populates="api_key")

    @classmethod
    def generate_api_key(cls, length: int = 256):
        """Generate a random API key."""
        return secrets.token_urlsafe(length)

    def __repr__(self):
        return f"ApiKey('{self.key}')"
