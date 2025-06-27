from typing import TYPE_CHECKING, Optional, cast

from sqlalchemy.exc import SQLAlchemyError

from app.logger import logger
from app.models.storyslide import StorySlide

from ..db import db

if TYPE_CHECKING:  # pragma: no cover
    from app.models.nightline import Nightline
    from app.models.status import Status


class NightlineStatus(db.Model):  # type: ignore
    __tablename__ = "nightline_statuses"
    id = db.Column(db.Integer, primary_key=True)
    nightline_id = db.Column(db.Integer, db.ForeignKey("nightlines.id"), nullable=False)
    nightline = db.relationship("Nightline", back_populates="nightline_statuses")
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=False)
    status = db.relationship("Status", backref="nightline_statuses")
    instagram_story = db.Column(db.Boolean, nullable=False, default=False)
    instagram_story_slide = db.relationship(StorySlide, back_populates="nightline_status", uselist=False)

    @classmethod
    def get_nightline_status(cls, nightline_id: int, status_id: int) -> Optional["NightlineStatus"]:
        nightline_status = cast(Optional["NightlineStatus"], NightlineStatus.query.filter_by(nightline_id=nightline_id, status_id=status_id).first())
        return nightline_status

    @classmethod
    def add_new_status_for_all_nightlines(cls, status: "Status") -> bool:
        from .nightline import Nightline

        """Create NightlineStatus entries for all Nightlines for a given Status"""
        logger.debug(f"Creating NightlineStatus entries for all nightlines with status '{status.name}'")

        nightlines = Nightline.list_nightlines()
        try:
            for nightline in nightlines:
                new_nightline_status = NightlineStatus(
                    nightline_id=nightline.id,
                    status_id=status.id,
                    instagram_story=False,  # Default to False for instagram story
                )
                db.session.add(new_nightline_status)
            db.session.commit()

            logger.info(f"NightlineStatus entries created successfully for status '{status.name}'")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating NightlineStatus entries for status '{status.name}': {e}")
            return False

    @classmethod
    def add_statuses_for_new_nightlines(cls, nightline: "Nightline") -> bool:
        from .status import Status

        """Create NightlineStatus entries for all Statuses for a nightline"""
        logger.debug(f"Creating NightlineStatus entries for all statuses for nightline '{nightline.name}'")

        statuses = Status.list_statuses()
        try:
            for status in statuses:
                new_nightline_status = NightlineStatus(
                    nightline_id=nightline.id,
                    status_id=status.id,
                    instagram_story=False,  # Default to False for instagram story
                )
                db.session.add(new_nightline_status)
            db.session.commit()

            logger.info(f"NightlineStatus entries created successfully for nightline '{nightline.name}'")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating NightlineStatus entries for nightline '{nightline.name}': {e}")
            return False

    @classmethod
    def delete_status_for_all_nightlines(cls, status: "Status") -> bool:
        """Delete the status from all nightlines by status"""
        logger.debug(f"Deleting NightlineStatus entries for status: '{status.name}'")

        try:
            # Delete all NightlineStatus entries that reference the given status
            rows_deleted = NightlineStatus.query.filter_by(status_id=status.id).delete()

            if rows_deleted > 0:
                db.session.commit()
                logger.info(f"Successfully deleted '{rows_deleted}' NightlineStatus entries for status: '{status.name}'")
                return True
            else:  # This would be an out of sync state as we have a status object but no nightline status objects for it
                logger.warning(f"No NightlineStatus entries found for status: '{status.name}'")
                return False
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting NightlineStatus entries for status: '{status.name}': {e}")
            return False

    @classmethod
    def delete_statuses_for_nightline(cls, nightline: "Nightline") -> bool:
        """Delete all statuses for a specific nightline"""
        logger.debug(f"Deleting all NightlineStatus entries for nightline: '{nightline.name}'")

        try:
            # Delete all NightlineStatus entries that reference the given nightline_id
            rows_deleted = NightlineStatus.query.filter_by(nightline_id=nightline.id).delete()

            if rows_deleted > 0:
                db.session.commit()
                logger.info(f"Successfully deleted '{rows_deleted}' NightlineStatus entries for nightline: '{nightline.name}'")
                return True
            else:  # This would be an out of sync state as we have a status object but no nightline status objects for it
                logger.warning(f"No NightlineStatus entries found for nightline: '{nightline.name}'")
                return False
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting NightlineStatus entries for nightline: '{nightline.name}': {e}")
            return False

    @classmethod
    def update_instagram_story(cls, nightline: "Nightline", status: "Status", instagram_story: bool) -> bool:
        """Update the instagram_story value for a specific nightline and status."""
        logger.debug(f"Updating instagram_story for nightline: '{nightline.name}' and status: '{status.name}' to '{instagram_story}'")

        try:
            nightline_status = NightlineStatus.query.filter_by(nightline_id=nightline.id, status_id=status.id).first()

            if nightline_status:
                nightline_status.instagram_story = instagram_story
                db.session.commit()
                logger.info(f"Updated instagram_story for nightline: '{nightline.name}', status: '{status.name}' to '{instagram_story}'")
                return True
            else:  # This would be an out of sync state as we have a status object but no nightline status objects for it
                logger.warning(f"No NightlineStatus entry found for nightline: '{nightline.name}' and status: {status.name}")
                return False
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating instagram_story for nightline: '{nightline.name}', status: '{status.name}': {e}")
            return False
