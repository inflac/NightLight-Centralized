import os
from pathlib import Path
from typing import Optional

from werkzeug.datastructures.file_storage import FileStorage

from app.logger import logger

ALLOWED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]


def validate_file_extension(file: FileStorage) -> Optional[str]:
    """Validate the a file extension"""
    if not isinstance(file, FileStorage) or not file.filename:
        return None

    if "." not in file.filename:
        return None

    extension = file.filename.rsplit(".", maxsplit=1)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        logger.warning(f"Invalid file extension for file: {file.filename}")
        return None
    return extension


def ensure_storage_path_exists(storage_path: Path) -> bool:
    """Ensure the storage path exists, creating it if necessary."""
    if not os.path.exists(storage_path):
        try:
            os.makedirs(storage_path)
            logger.info(f"Storage directory created at: {storage_path}")
            return True
        except OSError as e:
            logger.error(f"Error creating storage directory '{storage_path}': {e}")
            return False
    return True


def check_file_already_exists(base_file_path: Path) -> Optional[Path]:
    for ext in ALLOWED_IMAGE_EXTENSIONS:
        path = base_file_path.with_suffix(f".{ext}")
        if path.exists():
            logger.debug(f"Found an already existing file: '{path}'")
            return path
    return None


def save_file(file: FileStorage, file_path: Path) -> bool:
    """Save the file to the specified path."""
    try:
        file.save(file_path)
        logger.info(f"File saved successfully: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving file '{file_path}': {e}")
        return False


def remove_file(file_path: Path) -> bool:
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
