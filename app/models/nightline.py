from typing import Optional

from ..db import db
from .status import Status
from .apikey import ApiKey
from app.logger import logger


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

    @classmethod
    def get_nightline(cls, name: str) -> Optional["Nightline"]:
        """Query and return a nightline by name."""
        logger.debug(f"Fetching nightline by name: '{name}'")

        nightline = cls.query.filter_by(name=name).first()
        if nightline:
            logger.debug(f"Found nightline: '{name}'")
        else:
            logger.info(f"Nightline '{name}' not found")
        return nightline

    @classmethod
    def add_nightline(cls, name: str) -> Optional["Nightline"]:
        """Create a new nightline with the default status."""
        logger.debug(f"Adding new nightline: '{name}'")

        default_status = Status.get_status("default")
        if not default_status:
            logger.error(f"Nightline was not added because the default status is missing.")
            return None

        try:
            new_nightline = cls(name=name, status=default_status)
            db.session.add(new_nightline)
            db.session.commit()
            logger.debug(f"Created nightline: '{name}'")

            new_api_key = ApiKey(key=ApiKey.generate_api_key(), nightline_id=new_nightline.id)
            db.session.add(new_api_key)
            db.session.commit()
            logger.debug(f"Created API-Key for nightline: '{name}'")

            logger.info(f"Nightline '{name}' added successfully")
            return new_nightline
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding nightline '{name}': {str(e)}")
            return None

    @classmethod
    def remove_nightline(cls, name: str) -> Optional["Nightline"]:
        """Remove a nightline from the database."""
        logger.debug(f"Removing nightline: {name}")

        nightline = cls.get_nightline(name)
        if not nightline:
            logger.info(f"Nightline '{name}' not found, nothing to remove")
            return None

        try:
            db.session.delete(nightline)
            db.session.commit()

            logger.info(f"Nightline '{name}' removed successfully")
            return nightline
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing nightline '{name}': {str(e)}")
            return None

    @classmethod
    def list_nightlines(cls) -> list[dict]:
        """List all nightlines."""
        logger.debug("Listing all nightlines.")

        try:
            nightlines = cls.query.all()
            nightline_list = [{
                "id": nightline.id,
                "name": nightline.name,
                "status": nightline.status,
                "now": nightline.now,
            } for nightline in nightlines]

            logger.info(f"Listed {len(nightline_list)} nightlines")
            return nightline_list
        except Exception as e:
            logger.error(f"Error while fetching the nightlines: {str(e)}")
            raise RuntimeError(f"Error while fetching the nightlines: {str(e)}")

    def set_status(self, name: str) -> Optional[Status]:
        """Set the status of a nightline by the status name."""
        logger.debug(f"Set status of nightline '{self.name}' to: '{name}'")

        new_status = Status.get_status(name)
        if not new_status:
            return None

        self.status = new_status
        db.session.commit()

        logger.info(f"Status '{name}' set successfully.")
        return new_status

    def reset_status(self) -> Status:
        """Reset the status of a nightline to default."""
        logger.info(f"Reset the status of nightline: '{self.name}'")
        return self.set_status("default")

    def set_now(self, now: bool) -> None:
        """Set now value of a nightline."""
        logger.info(f"Set the now value of nightline: '{self.name}' to: '{now}'")
        self.now = now
        db.session.commit()

    def get_api_key(self) -> Optional[ApiKey]:
        """Get the API key."""
        return ApiKey.get_api_key(self.id)

    def renew_api_key(self) -> bool:
        """Generate and assign a new 256B API key to the nightline."""
        logger.debug(f"Renew api key of nightline: '{self.name}'")

        api_key =  ApiKey.get_api_key(self.id)
        if api_key:
            api_key.key = ApiKey.generate_api_key()
            db.session.commit()

            logger.info(f"Api key for nightline '{self.name}' renewed successfully")
            return True
        
        logger.error(f"No api key found for nightline: '{self.name}'")
        return False

    def __repr__(self) -> str:
        return f"Nightline('{self.name}')"
