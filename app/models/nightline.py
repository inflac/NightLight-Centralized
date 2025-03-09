from typing import Optional
from sqlalchemy import or_

from ..db import db
from .status import Status
from .apikey import ApiKey
from .nightlinestatus import NightlineStatus
from .instagram import InstagramAccount
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
    nightline_statuses = db.relationship(
        "NightlineStatus",
        back_populates="nightline",
        cascade="all, delete-orphan")
    now = db.Column(db.Boolean, nullable=False, default=False)
    instagram_media_id = db.Column(db.String(50), nullable=True, default="")
    instagram_account = db.relationship(
        "InstagramAccount",
        uselist=False,
        cascade="all, delete-orphan",
        back_populates="nightline")

    @classmethod
    def get_nightline(cls, name: str) -> Optional["Nightline"]:
        """Query and return a nightline by name"""
        logger.debug(f"Fetching nightline by name: '{name}'")

        nightline = cls.query.filter_by(name=name).first()
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
            logger.error(
                f"Nightline was not added because the default status is missing")
            return None

        try:
            new_nightline = cls(name=name, status=default_status)
            db.session.add(new_nightline)
            db.session.commit()
            logger.debug(f"Created nightline: '{name}'")

            new_api_key = ApiKey(
                key=ApiKey.generate_api_key(),
                nightline_id=new_nightline.id)
            db.session.add(new_api_key)
            db.session.commit()
            logger.debug(f"Created API-Key for nightline: '{name}'")

            # Create NightlineStatus entries for all Statuses
            NightlineStatus.add_statuses_for_new_nightlines(new_nightline)

            logger.info(f"Nightline '{name}' added successfully")
            return new_nightline
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding nightline '{name}': {str(e)}")
            return None

    @classmethod
    def remove_nightline(cls, name: str) -> Optional["Nightline"]:
        """Remove a nightline from the database"""
        logger.debug(f"Removing nightline: {name}")

        nightline = cls.get_nightline(name)
        if not nightline:
            logger.info(f"Nightline '{name}' not found, nothing to remove")
            return None

        api_key = ApiKey.get_api_key(nightline.id)
        if not api_key:
            logger.info(
                f"Api key for nightline '{name}' not found, can't remove the nightline")
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
            db.session.rollback()
            logger.error(f"Error removing nightline '{name}': {str(e)}")
            return None

    @classmethod
    def list_nightlines(cls, status_filter: str = None, language_filter: str = None,
                        now_filter: bool = None) -> list["Nightline"]:
        """List all nightlines with optional filters"""
        logger.debug("Listing all nightlines with filters")

        try:
            query = cls.query.join(Status, Nightline.status)

            # Apply filters if provided
            if status_filter:
                query = query.filter(Nightline.status.has(name=status_filter))

            if language_filter:
                if language_filter == "de":
                    query = query.filter(
                        or_(
                            Status.name == "german",
                            Status.name == "german-english"
                        )
                    )
                elif language_filter == "en":
                    query = query.filter(
                        or_(
                            Status.name == "english",
                            Status.name == "german-english"
                        )
                    )

            if isinstance(now_filter, bool):
                query = query.filter(Nightline.now == now_filter)

            # Fetch nightlines that match filter criteria
            nightlines = query.all()

            logger.info(f"Listed {len(nightlines)} nightlines")
            return nightlines

        except Exception as e:
            logger.error(f"Error while fetching the nightlines: {str(e)}")
            raise RuntimeError(
                f"Error while fetching the nightlines: {
                    str(e)}")

    def set_status(self, name: str) -> Optional[Status]:
        """Set the status of a nightline by the status name"""
        logger.debug(f"Set status of nightline '{self.name}' to: '{name}'")

        new_status = Status.get_status(name)
        if not new_status:
            return None

        self.status = new_status
        db.session.commit()

        logger.info(f"Status '{name}' set successfully")
        return new_status

    def reset_status(self) -> Status:
        """Reset the status of a nightline to default"""
        logger.info(f"Reset the status of nightline: '{self.name}'")
        return self.set_status("default")

    def get_instagram_story_config(self) -> Optional[bool]:
        """Get the Instagram story config for the current status"""
        for nightline_status in self.nightline_statuses:
            if nightline_status.status_id == self.status_id:
                return nightline_status.instagram_story
        return None

    def set_now(self, now: bool) -> None:
        """Set now value of a nightline"""
        logger.info(
            f"Set the now value of nightline: '{
                self.name}' to: '{now}'")
        self.now = now
        db.session.commit()

    def get_api_key(self) -> Optional[ApiKey]:
        """Get the API key"""
        return ApiKey.get_api_key(self.id)

    def renew_api_key(self) -> bool:
        """Generate and assign a new 256B API key to the nightline"""
        logger.debug(f"Renew api key of nightline: '{self.name}'")

        api_key = ApiKey.get_api_key(self.id)
        if api_key:
            api_key.key = ApiKey.generate_api_key()
            db.session.commit()

            logger.info(
                f"Api key for nightline '{
                    self.name}' renewed successfully")
            return True

        logger.error(f"No api key found for nightline: '{self.name}'")
        return False

    def add_instagram_account(self, username: str, password: str) -> bool:
        """Creates an Instagram account for the Nightline and saves it."""
        if not self.instagram_account:
            insta_account = InstagramAccount(
                nightline_id=self.id, username=username)
            # Automatically encrypts and saves the password
            insta_account.set_password(password)
            db.session.add(insta_account)
            db.session.commit()

            logger.info(
                f"Instagram account added for nightline {
                    self.name} with username {username}")
            return True
        else:
            logger.warning(
                f"Instagram account already exists for nightline {
                    self.name}")
            return False

    def update_instagram_username(self, new_username: str) -> bool:
        """Updates the Instagram account's username."""
        if self.instagram_account:
            self.instagram_account.set_username(new_username)
            db.session.commit()

            logger.info(
                f"Instagram username updated to {new_username} for Nightline {
                    self.name}.")
            return True
        else:
            logger.warning(
                f"No Instagram account found for Nightline {
                    self.name}.")
            return False

    def update_instagram_password(self, new_password: str) -> bool:
        """Updates the Instagram account's password."""
        if self.instagram_account:
            self.instagram_account.set_password(new_password)
            db.session.commit()

            logger.info(
                f"Instagram password updated for Nightline {
                    self.name}.")
            return True
        else:
            logger.warning(
                f"No Instagram account found for Nightline {
                    self.name}.")
            return False

    def delete_instagram_account(self) -> bool:
        """Deletes the associated Instagram account."""
        if self.instagram_account:
            db.session.delete(self.instagram_account)
            db.session.commit()

            logger.info(
                f"Instagram account deleted for Nightline {
                    self.name}.")
            return True
        else:
            logger.warning(
                f"No Instagram account found for Nightline {
                    self.name}.")
            return False

    def __repr__(self) -> str:
        return f"Nightline('{self.name}')"
