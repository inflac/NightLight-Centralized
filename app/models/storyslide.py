import os
from typing import Optional

from ..db import db
from app.config import Config
from app.logger import logger


class StorySlide(db.Model):
    __tablename__ = 'storyslides'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(20)) # max length = max status name + . + file extension = 15 + 1 + 3
    path = db.Column(db.String(100)) # max length = ./instance/nightlines/[22] nl-xy[50] /[1] status[15] .png[4] = 92
    nightline_status_id = db.Column(
        db.Integer,
        db.ForeignKey("nightline_statuses.id"),
        unique=True,
        nullable=False)
    nightline_status = db.relationship("NightlineStatus", back_populates="instagram_story_slide")

    @staticmethod
    def __validate_file_extension(file) -> Optional[str]:
        """Validate the file extension to ensure it's an allowed image type."""
        allowed_extensions = ["png", "jpg", "jpeg"]
        extension = file.filename.rsplit(".", maxsplit=1)[1].lower()
        if extension not in allowed_extensions:
            logger.warning(f"Invalid file extension for file: {file.filename}")
            return None
        return extension

    @staticmethod
    def __ensure_storage_path_exists(storage_path: str) -> bool:
        """Ensure the storage path exists, creating it if necessary."""
        if not os.path.exists(storage_path):
            try:
                os.makedirs(storage_path)
                logger.info(f"Directory created at: {storage_path}")
                return True
            except OSError as e:
                logger.error(f"Error creating directory '{storage_path}': {e}")
                return False
        return True

    @staticmethod
    def __check_if_file_exists(base_file_path: os.PathLike, allowed_extensions: list) -> Optional[os.PathLike]:
        """Check if a file with the same base name already exists."""
        for ext in allowed_extensions:
            path = f"{base_file_path}.{ext}"
            if os.path.exists(path):
                logger.debug(f"Found an already existing file: '{base_file_path}'")
                return path
        return None

    @staticmethod
    def __save_file(file, file_path: os.PathLike) -> bool:
        """Save the file to the specified path."""
        try:
            file.save(file_path)
            logger.info(f"File saved successfully: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving file '{file_path}': {e}")
            return False

    @staticmethod
    def __remove_file(file_path: os.PathLike) -> bool:
        """Safely remove a file from the filesystem"""

        if not os.path.exists(file_path):
            logger.warning(f"File '{file_path}' does not exist")
            return False

        try:
            os.remove(file_path)
            logger.info(f"File '{file_path}' removed successfully")
            return True
        except Exception as e:
            logger.error(f"Error removing file '{file_path}': {e}")
            return False

    @classmethod
    def get_story_slide_by_nightline_status(cls, nightline_status: "NightlineStatus"):
        """Fetch a story slide by a nightline status"""
        logger.debug(f"Fetching story slide for nightline status with ID: '{nightline_status.id}'")
        story_slide = cls.query.filter_by(nightline_status_id=nightline_status.id).first()
        if story_slide:
            logger.debug(f"Found story slide for status '{nightline_status.status.name}' of nightline '{nightline_status.nightline.name}'")
        else:
            logger.info(f"Story Slide for nightline status '{nightline_status.status.name}' of nightline '{nightline_status.nightline.name}' not found")
        return story_slide

    @classmethod
    def __save_story_slide_file(cls, file, nightline_status: "NightlineStatus", overwrite=False) -> Optional[os.PathLike]:
        """Handles saving the file and checks if the file already exists."""
        
        # Validate file type
        extension = cls.__validate_file_extension(file)
        if not extension:
            return None

        # Construct base filename and storage path
        base_filename = nightline_status.status.name
        filename = f"{base_filename}.{extension}"
        storage_path = os.path.join(Config.UPLOAD_FOLDER, nightline_status.nightline.name)

        # Ensure the storage path exists
        if not cls.__ensure_storage_path_exists(storage_path):
            return None

        # Check if a file with the same base name already exists
        base_file_path = os.path.join(storage_path, base_filename)
        existing_file_path = cls.__check_if_file_exists(base_file_path, ["png", "jpg", "jpeg"])
        if existing_file_path:
            if overwrite:
                logger.debug(f"Replacing the already existing story slide: '{existing_file_path}' for status: '{nightline_status.status.name}'")
                cls.__remove_file(existing_file_path)
            else:
                logger.info(f"Found an existing story slide for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}'")
                return None

        # Save the file to the storage path
        file_path = os.path.join(storage_path, filename)
        if cls.__save_file(file, file_path):
            return file_path
        return None

    @classmethod
    def update_story_slide(cls, file, nightline_status: "NightlineStatus") -> Optional["StorySlide"]:
        """Create a story slide object, referencing the file and filepath"""

        # Save the file and get the file path
        file_path = cls.__save_story_slide_file(file, nightline_status, overwrite=True)
        if not file_path:
            return None

        # Create or update the StorySlide object and save it to the database
        try:
            story_slide = StorySlide.get_story_slide_by_nightline_status(nightline_status)
            if not story_slide:
                story_slide = cls(filename=os.path.basename(file_path), path=file_path, nightline_status_id=nightline_status.id)
                db.session.add(story_slide)
            else:
                story_slide.filename = os.path.basename(file_path)
                story_slide.path = file_path
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
        file_path = nightline_status.story_slide.path
        if os.path.exists(file_path):
            if not cls.__remove_file(file_path):
                return False
        
        try:
            db.session.delete(nightline_status.story_slide)
            db.session.commit()

            logger.info("for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}' removed successfully")
            return True
        except Exception as e:
            logger.error(f"Error removing StorySlide for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}': {e}")
            return False