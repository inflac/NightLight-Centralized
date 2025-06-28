import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, cast

from werkzeug.datastructures.file_storage import FileStorage

from app.config import Config
from app.db import db
from app.filehandler import (
    check_file_already_exists,
    ensure_storage_path_exists,
    remove_file,
    save_file,
    validate_file_extension,
)
from app.logger import logger

if TYPE_CHECKING:  # pragma: no cover
    from app.models.nightlinestatus import NightlineStatus


class StorySlide(db.Model):  # type: ignore
    __tablename__ = "storyslides"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(20))  # max length = max status name + . + file extension = 15 + 1 + 3
    path = db.Column(db.String(100))  # max length = ./instance/nightlines/[22] nl-xy[50] /[1] status[15] .png[4] = 92
    nightline_status_id = db.Column(db.Integer, db.ForeignKey("nightline_statuses.id"), unique=True, nullable=False)
    nightline_status = db.relationship("NightlineStatus", back_populates="instagram_story_slide")

    @classmethod
    def _save_story_slide_file(cls, file: FileStorage, nightline_status: "NightlineStatus", overwrite: bool = False) -> Optional[Path]:
        """Handles saving the file and checks if the file already exists."""

        # Validate file type
        extension = validate_file_extension(file)
        if not extension:
            return None

        # Create and ensure the storage path exists
        storage_path = Path(os.path.join(Config.UPLOAD_FOLDER, nightline_status.nightline.name))
        if not ensure_storage_path_exists(storage_path):
            return None

        # Construct base filename and base file path
        base_filename = nightline_status.status.name
        base_file_path = os.path.join(storage_path, base_filename)

        # Check if a story slide for the selected status already exists
        existing_file_path = check_file_already_exists(Path(base_file_path))
        if existing_file_path:
            if overwrite:
                logger.debug(f"Replacing the already existing story slide: '{existing_file_path}' for status: '{nightline_status.status.name}'")
                remove_file(existing_file_path)
            else:
                logger.warning(f"Found an existing story slide for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}'")
                return None

        # Save the file to the storage path
        filename = f"{base_filename}.{extension}"
        file_path = Path(os.path.join(storage_path, filename))
        if save_file(file, file_path):
            return file_path
        return None

    @classmethod
    def get_story_slide_by_nightline_status(cls, nightline_status: "NightlineStatus") -> Optional["StorySlide"]:
        """Fetch a story slide by a nightline status"""
        logger.debug(f"Fetching story slide for nightline status with ID: '{nightline_status.id}'")

        story_slide = cast(Optional["StorySlide"], cls.query.filter_by(nightline_status_id=nightline_status.id).first())
        if story_slide:
            logger.debug(f"Found story slide for status '{nightline_status.status.name}' of nightline '{nightline_status.nightline.name}'")
        else:
            logger.info(f"Story Slide for nightline status '{nightline_status.status.name}' of nightline '{nightline_status.nightline.name}' not found")
        return story_slide

    @classmethod
    def update_story_slide(cls, file: FileStorage, nightline_status: "NightlineStatus") -> Optional["StorySlide"]:
        """Create a story slide object, referencing the file and filepath"""
        # Save the file and get the file path
        file_path = cls._save_story_slide_file(file, nightline_status, overwrite=True)
        if not file_path:
            return None

        # Create or update the StorySlide object and save it to the database
        try:
            story_slide = StorySlide.get_story_slide_by_nightline_status(nightline_status)
            if not story_slide:
                story_slide = cls(
                    filename=os.path.basename(file_path),
                    path=str(file_path),
                    nightline_status_id=nightline_status.id,
                )
                db.session.add(story_slide)
            else:
                story_slide.filename = os.path.basename(file_path)
                story_slide.path = str(file_path)
            db.session.commit()

            logger.info(f"StorySlide for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}' updated successfully")
            return story_slide
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating StorySlide for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}': {e}")
            return None

    @classmethod
    def remove_story_slide(cls, nightline_status: "NightlineStatus") -> bool:
        """Remove a story slide for a nightlines status"""
        status_name = nightline_status.status.name
        nightline_name = nightline_status.nightline.name

        if not nightline_status.instagram_story_slide:
            logger.warning(f"No story slide found for status: '{status_name}' of nightline: '{nightline_name}'")
            return False
        
        slide_path = nightline_status.instagram_story_slide.path

        if not remove_file(slide_path):
            logger.warning(f"Failed to remove file at path: '{slide_path}' for status: '{status_name}' of nightline: '{nightline_name}'")
            return False

        try:
            db.session.delete(nightline_status.instagram_story_slide)
            db.session.commit()
            logger.info(f"StorySlide for status: '{status_name}' of nightline: '{nightline_name}' removed successfully")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing StorySlide from DB for status: '{status_name}' of nightline: '{nightline_name}': {e}")
            return False
