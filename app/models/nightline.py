from typing import Optional

from ..db import db
from .status import Status
from .apikey import ApiKey

class Nightline(db.Model):
    __tablename__ = "nightlines"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    status_id = db.Column(
        db.Integer,
        db.ForeignKey("statuses.id"),
        nullable=False)
    status = db.relationship("Status", backref="nightlines")
    now = db.Column(db.Boolean, nullable=False, default=False)
    instagram_media_id = db.Column(db.String(50), nullable=True, default="")

    api_key = db.relationship(
        "ApiKey",
        uselist=False,
        back_populates="nightline")

    @classmethod
    def get_nightline(cls, name: str) -> Optional["Nightline"]:
        """Query and return a nightline by name."""
        nightline = Nightline.query.filter_by(name=name).first()
        return nightline

    @classmethod
    def add_nightline(cls, name: str) -> Optional["Nightline"]:
        """Create a new nightline with the default status."""
        default_status = Status.get_status("default")
        if not default_status:
            return

        try:
            new_nightline = cls(name=name, status=default_status)
            api_key = ApiKey(key=ApiKey.generate_api_key())
            new_nightline.api_key = api_key

            db.session.add(new_nightline)
            db.session.commit()
            return new_nightline
        except Exception as e:
            db.session.rollback()
            return

    @classmethod
    def remove_nightline(cls, name: str) -> Optional["Nightline"]:
        """Remove a nightline from the database."""
        nightline = Nightline.get_nightline(name)
        if not nightline:
            return

        try:
            db.session.delete(nightline)
            db.session.commit()
            nightline
        except Exception as e:
            db.session.rollback()
            return

    @classmethod
    def list_nightlines(cls) -> list[dict]:
        """List all nightlines."""
        try:
            nightlines = Nightline.query.all()
            nightline_list = [{
                "id": nightline.id,
                "name": nightline.name,
                "status": nightline.status,
                "now": nightline.now,
            } for nightline in nightlines]
            return nightline_list
        except Exception as e:
            raise RuntimeError(f"Error while fetching the cities: {str(e)}")

    def set_status(self, name: str) -> Optional[Status]:
        """Set the status of a nightline by the status name."""
        new_status = Status.get_status(name)
        if not new_status:
            return
        
        self.status = new_status
        db.session.commit()

        return new_status

    def reset_status(self) -> Status:
        """Reset the status of a nightline to default."""
        return self.reset_status("default")

    def set_now(self, now: bool) -> None:
        """Set now value of a nightline."""
        self.now = now
        db.session.commit()

    def get_api_key(self):
        """Get the API key."""
        if self.api_key:
            return self.api_key.key
        return None

    def renew_api_key(self):
        """Generate and assign a new 256B API key to the nightline."""
        if self.api_key:
            # Generate a new key and update the existing record
            self.api_key.key = ApiKey.generate_api_key()
        else:
            # If no API key exists, create a new one
            self.api_key = ApiKey(key=ApiKey.generate_api_key())
        db.session.commit()

    def __repr__(self) -> str:
        return f"Nightline('{self.name}')"
