from typing import List, Optional, cast

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app.logger import logger
from app.story_post import delete_story_by_id, post_story

from ..db import db
from .apikey import ApiKey
from .instagram import InstagramAccount
from .nightlinestatus import NightlineStatus
from .status import Status


class Nightline(db.Model):  # type: ignore
    __tablename__ = "nightlines"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=False)
    status = db.relationship("Status", backref="nightlines")
    nightline_statuses = db.relationship("NightlineStatus", back_populates="nightline", cascade="all, delete-orphan")
    now = db.Column(db.Boolean, nullable=False, default=False)
    instagram_media_id = db.Column(db.String(50), nullable=True, default="")
    instagram_account = db.relationship(
        "InstagramAccount",
        uselist=False,
        cascade="all, delete-orphan",
        back_populates="nightline",
    )

    @classmethod
    def get_nightline(cls, name: str) -> Optional["Nightline"]:
        """Query and return a nightline by name"""
        logger.debug(f"Fetching nightline by name: '{name}'")

        nightline = cast(Optional["Nightline"], cls.query.filter_by(name=name).first())
        if nightline:
            logger.debug(f"Found nightline: '{name}'")
        else:
            logger.info(f"Nightline '{name}' not found")
        return nightline

    @classmethod
    def add_nightline(cls, name: str) -> Optional["Nightline"]:
        """Create a new nightline with the default status"""
        logger.debug(f"Adding new nightline: '{name}'")

        default_status = Status.get_status("default")
        if not default_status:
            logger.error(f"Nightline was not added because the default status is missing")
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

            # Create NightlineStatus entries for all Statuses
            NightlineStatus.add_statuses_for_new_nightlines(new_nightline)

            logger.info(f"Nightline '{name}' added successfully")
            return new_nightline
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding nightline '{name}': {e}")
            return None

    @classmethod
    def remove_nightline(cls, name: str) -> Optional["Nightline"]:
        """Remove a nightline from the database"""
        logger.debug(f"Removing nightline: '{name}'")

        nightline = cls.get_nightline(name)
        if not nightline:
            logger.info(f"Nightline '{name}' not found, nothing to remove")
            return None

        api_key = ApiKey.get_api_key(nightline.id)
        if not api_key:  # This would be an out-of-sync state where the nightline exists but no API-Key. Might occure on previous exception in deletetion
            logger.warning(f"Api key for nightline '{name}' not found, can't remove the nightline")
            return None

        NightlineStatus.delete_statuses_for_nightline(nightline)

        try:
            db.session.delete(api_key)
            db.session.commit()
            logger.debug(f"Removed api key for nightline: '{name}'")

            db.session.delete(nightline)
            db.session.commit()

            logger.info(f"Nightline '{name}' removed successfully")
            return nightline
        except Exception as e:
            NightlineStatus.add_statuses_for_new_nightlines(nightline)  # Re-add the statuses to prevent getting out of sync
            db.session.rollback()
            logger.error(f"Error removing nightline '{name}': {e}")
            return None

    @classmethod
    def list_nightlines(
        cls,
        status_filter: Optional[str] = None,
        language_filter: Optional[str] = None,
        now_filter: Optional[bool] = None,
    ) -> list["Nightline"]:
        """List all nightlines with optional filters"""
        logger.debug("Listing all nightlines with filters")

        try:
            query = cls.query.join(Status, Nightline.status)

            # Apply filters if provided
            if status_filter:
                query = query.filter(Nightline.status.has(name=status_filter))

            if language_filter:
                if language_filter == "de":
                    query = query.filter(or_(Status.name == "german", Status.name == "german-english"))
                elif language_filter == "en":
                    query = query.filter(or_(Status.name == "english", Status.name == "german-english"))

            if isinstance(now_filter, bool):
                query = query.filter(Nightline.now == now_filter)

            # Fetch nightlines that match filter criteria
            nightlines = cast(list[Nightline], query.all())

            logger.info(f"Listed {len(nightlines)} nightlines")
            return nightlines

        except Exception as e:
            logger.error(f"Error while fetching the nightlines: {e}")
            return []

    def set_status(self, name: str) -> bool:
        """Set the status of a nightline by the status name"""
        logger.debug(f"Set status of nightline '{self.name}' to: '{name}'")

        try:
            new_status = Status.get_status(name)
            if not new_status:
                logger.info(f"Status '{name}' not found. Status not changed")
                return False

            self.status = new_status
            db.session.commit()

            logger.info(f"Status '{name}' set successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set status '{name}' for nightline '{self.name}': {e}")
            db.session.rollback()
            return False

    def reset_status(self) -> bool:
        """Reset the status of a nightline to default"""
        logger.info(f"Reset the status of nightline: '{self.name}'")
        return self.set_status("default")

    def set_now(self, now: bool) -> bool:
        """Set now value of a nightline"""
        try:
            logger.info(f"Set the now value of nightline: '{self.name}' to: '{now}'")
            self.now = now
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to set now value for nightline '{self.name}' to '{now}': {e}")
            db.session.rollback()
            return False

    def get_instagram_story_config(self) -> bool:
        """Get the Instagram story config for the current status"""
        nightline_status = NightlineStatus.get_nightline_status(nightline_id=self.id, status_id=self.status.id)
        if nightline_status:
            return cast(bool, nightline_status.instagram_story)
        return False

    def set_instagram_media_id(self, media_id: Optional[str]) -> bool:
        logger.debug(f"Setting media id for a status of nightline '{self.name}'")
        try:
            self.instagram_media_id = media_id
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error while setting Instagram media id for nightline '{self.name}': {e}")
            db.session.rollback()
            return False

    def get_api_key(self) -> Optional[ApiKey]:
        """Get the API key"""
        return ApiKey.get_api_key(self.id)

    def renew_api_key(self) -> bool:
        """Generate and assign a new 256B API key to the nightline"""
        logger.debug(f"Renew api key of nightline: '{self.name}'")

        api_key = ApiKey.get_api_key(self.id)
        if not api_key:
            logger.warning(f"No API key found for nightline: '{self.name}'")
            return False

        try:
            api_key.key = ApiKey.generate_api_key()
            db.session.commit()

            logger.info(f"API key for nightline '{self.name}' renewed successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error while renewing API key for nightline '{self.name}': {e}")
            db.session.rollback()
            return False

    def add_instagram_account(self, username: str, password: str) -> bool:
        """Creates an Instagram account for the Nightline and saves it."""
        if self.instagram_account:
            logger.warning(f"Instagram account already exists for nightline '{self.name}'")
            return False

        try:
            insta_account = InstagramAccount(nightline_id=self.id, username=username)
            insta_account.set_password(password)  # Assumes password is encrypted internally
            db.session.add(insta_account)
            db.session.commit()

            logger.info(f"Instagram account added for nightline '{self.name}' with username '{username}'")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error while adding Instagram account for nightline '{self.name}': {e}")
            db.session.rollback()
            return False

    def update_instagram_username(self, new_username: str) -> bool:
        """Updates the Instagram account's username."""
        if not self.instagram_account:
            logger.warning(f"No Instagram account configured for nightline '{self.name}'.")
            return False

        try:
            self.instagram_account.set_username(new_username)
            db.session.commit()

            logger.info(f"Instagram username updated to '{new_username}' for Nightline '{self.name}'.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error while updating username of Instagram account for nightline '{self.name}': {e}")
            db.session.rollback()
            return False

    def update_instagram_password(self, new_password: str) -> bool:
        """Updates the Instagram account's password."""
        if not self.instagram_account:
            logger.warning(f"No Instagram account configured for nightline '{self.name}'.")
            return False

        try:
            self.instagram_account.set_password(new_password)
            db.session.commit()

            logger.info(f"Instagram password updated for Nightline '{self.name}'.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error while updating password of Instagram account for nightline '{self.name}': {e}")
            db.session.rollback()
            return False

    def delete_instagram_account(self) -> bool:
        """Deletes the associated Instagram account."""
        if not self.instagram_account:
            logger.warning(f"No Instagram account configured for nightline '{self.name}'.")
            return False

        try:
            db.session.delete(self.instagram_account)
            db.session.commit()

            logger.info(f"Instagram account deleted for Nightline '{self.name}'.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting Instagram account of nightline '{self.name}': {e}")
            db.session.rollback()
            return False

    def post_instagram_story(self, status_name: str) -> bool:
        if not self.instagram_account:
            logger.warning(f"No Instagram account configured for nightline '{self.name}'.")
            return False

        status = Status.get_status(status_name)
        if not status:
            logger.warning(f"No status with name '{status_name}' found.")
            return False

        nightline_status = NightlineStatus.get_nightline_status(nightline_id=self.id, status_id=status.id)

        if not nightline_status:
            logger.warning(f"NightlineStatus not found for status '{status_name}' and nightline '{self.name}'.")
            return False

        # Check if posting an Instagram story is configured
        if not nightline_status.instagram_story:
            logger.info(f"Posting an Instagram story is not configured for status '{status_name}' of nightline '{self.name}'.")
            return False

        # Check if a story slide is configured
        if not nightline_status.instagram_story_slide:
            logger.info(f"No Instagram story slide configured for status '{status_name}' of nightline '{self.name}'.")
            return False

        # Post the story
        instagram_username = self.instagram_account.username
        instagram_password = self.instagram_account.get_password()
        story_slide_path = nightline_status.instagram_story_slide.path
        media_id = post_story(story_slide_path, instagram_username, instagram_password)
        if media_id and self.set_instagram_media_id(media_id):
            logger.info(f"Successfully posted Instagram story for status '{status_name}' of nightline '{self.name}'.")
            return True
        else:
            logger.error(f"Failed to post Instagram story (no media ID returned) for nightline '{self.name}'.")
            return False

    def delete_instagram_story(self) -> bool:
        if not self.instagram_media_id:
            logger.debug("No story to delete because no media id is set")
            return True

        if not self.instagram_account:
            logger.warning(f"No Instagram account configured for nightline '{self.name}'.")
            return False

        username = self.instagram_account.username
        password = self.instagram_account.get_password()

        if not delete_story_by_id(self.instagram_media_id, username, password):
            logger.error(f"Failed to delete Instagram story with media ID '{self.instagram_media_id}' for nightline '{self.name}'.")
            return False

        if not self.set_instagram_media_id(None):
            logger.error(f"Story deleted but failed to unset media ID for nightline '{self.name}'.")
            return False

        logger.info(f"Successfully deleted Instagram story for nightline '{self.name}'.")
        return True

    def __repr__(self) -> str:
        return f"Nightline('{self.name}')"
