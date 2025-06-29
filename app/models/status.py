from typing import List, Optional, cast

from app.logger import logger

from ..db import db
from .nightlinestatus import NightlineStatus


class Status(db.Model):  # type: ignore
    __tablename__ = "statuses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    description_de = db.Column(db.String(200), nullable=False)
    description_en = db.Column(db.String(200), nullable=False)
    description_now_de = db.Column(db.String(200), nullable=False)
    description_now_en = db.Column(db.String(200), nullable=False)

    @classmethod
    def get_status(cls, name: str) -> Optional["Status"]:
        """Query and return a status by name"""
        logger.debug(f"Fetching status by name: {name}")

        status = cast(Optional["Status"], cls.query.filter_by(name=name).first())
        if status:
            logger.debug(f"Found status: {name}")
        else:
            logger.info(f"Status '{name}' not found")
        return status

    @classmethod
    def add_status(
        cls,
        name: str,
        description_de: str,
        description_en: str,
        description_now_de: str,
        description_now_en: str,
    ) -> Optional["Status"]:
        """Add a new status to the db"""
        logger.debug(f"Adding new status: {name}")

        if cls.query.filter_by(name=name).first():
            logger.warning(f"Status '{name}' already exists")
            return None

        try:
            new_status = Status(
                name=name,
                description_de=description_de,
                description_en=description_en,
                description_now_de=description_now_de,
                description_now_en=description_now_en,
            )
            db.session.add(new_status)
            db.session.commit()

            # Create NightlineStatus entries for all Nightlines
            NightlineStatus.add_new_status_for_all_nightlines(new_status)

            logger.info(f"Status '{name}' added successfully")
            return new_status
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding status '{name}': {e}")
            return None

    @classmethod
    def remove_status(cls, name: str) -> Optional["Status"]:
        """Remove a status from the db by its name"""
        logger.debug(f"Removing status: {name}")

        status_to_remove = Status.get_status(name)
        if not status_to_remove:
            logger.warning(f"Status '{name}' not found, nothing to remove")
            return None

        NightlineStatus.delete_status_for_all_nightlines(status_to_remove)

        try:
            db.session.delete(status_to_remove)
            db.session.commit()

            logger.info(f"Status '{name}' removed successfully")
            return status_to_remove
        except Exception as e:
            db.session.rollback()
            NightlineStatus.add_new_status_for_all_nightlines(status_to_remove)  # Re-add status to nls to prevent an out of sync state
            logger.error(f"Error removing status '{name}': {e}")
            return None

    @classmethod
    def list_statuses(cls) -> list["Status"]:
        """List all available statuses"""
        logger.debug("Listing all statuses")

        try:
            statuses = cast(List["Status"], Status.query.all())

            logger.info(f"Listed {len(statuses)} statuses")
            return statuses
        except Exception as e:
            logger.error(f"Error while fetching the statuses: {e}")
            return []

    def __repr__(self) -> str:
        return f"Status('{self.name}')"
