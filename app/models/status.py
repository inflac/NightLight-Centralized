from typing import Optional

from ..db import db
from app.logger import logger


class Status(db.Model):
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    description_de = db.Column(db.String(200), nullable=False)
    description_en = db.Column(db.String(200), nullable=False)
    description_now_de = db.Column(db.String(200), nullable=False)
    description_now_en = db.Column(db.String(200), nullable=False)

    @classmethod
    def get_status(cls, name: str) -> Optional["Status"]:
        """Query and return a status by name."""
        logger.debug(f"Fetching status by name: {name}")

        status = cls.query.filter_by(name=name).first()
        if status:
            logger.debug(f"Found status: {name}")
        else:
            logger.info(f"Status '{name}' not found.")
        return status

    @classmethod
    def add_status(cls, name: str, description_de: str, description_en: str,
                   description_now_de: str, description_now_en: str) -> Optional["Status"]:
        """Add a new status to the db."""
        logger.debug(f"Adding new status: {name}")

        if cls.query.filter_by(name=name).first():
            logger.error(f"Status '{name}' already exists.")
            raise ValueError(f"Status '{name}' already exists.")

        try:
            new_status = Status(
                name=name,
                description_de=description_de,
                description_en=description_en,
                description_now_de=description_now_de,
                description_now_en=description_now_en)
            db.session.add(new_status)
            db.session.commit()

            logger.info(f"Status '{name}' added successfully.")
            return new_status
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding status '{name}': {str(e)}")
            return None

    @classmethod
    def remove_status(cls, name: str) -> Optional["Status"]:
        """Remove a status from the db by its name."""
        logger.debug(f"Removing status: {name}")

        status_to_remove = Status.get_status(name)
        if not status_to_remove:
            logger.info(f"Status '{name}' not found, nothing to remove.")
            return None

        try:
            db.session.delete(status_to_remove)
            db.session.commit()

            logger.info(f"Status '{name}' removed successfully.")
            return status_to_remove
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing status '{name}': {str(e)}")
            return None

    @classmethod
    def list_status(cls) -> list[dict]:
        """List all available statuses."""
        logger.debug("Listing all statuses.")

        try:
            statuses = Status.query.all()
            status_list = [{
                "name": status.name,
                "description_de": status.description_de,
                "description_en": status.description_en,
                "description_now_de": status.description_now_de,
                "description_now_en": status.description_now_en,
            } for status in statuses]

            logger.info(f"Listed {len(status_list)} statuses.")
            return status_list
        except Exception as e:
            logger.error(f"Error while fetching the statuses: {str(e)}")
            raise RuntimeError(f"Error while fetching the statuses: {str(e)}")

    def __repr__(self) -> str:
        return f"Status('{self.name}')"
