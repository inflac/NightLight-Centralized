import os

from typing import Optional
from werkzeug.datastructures.file_storage import FileStorage

from app.logger import logger


ALLOWED_IMAGE_EXTENSIONS=["png", "jpg", "jpeg"]


def validate_file_extension(file: FileStorage) -> Optional[str]:
    """Validate the a file extension"""
    extension = file.filename.rsplit(".", maxsplit=1)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        logger.warning(f"Invalid file extension for file: {file.filename}")
        return None
    return extension

def ensure_storage_path_exists(storage_path: str) -> bool:
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

def check_file_already_exists(base_file_path: os.PathLike) -> Optional[os.PathLike]:
    """Check if a file with the same base name already exists."""
    for ext in ALLOWED_IMAGE_EXTENSIONS:
        path = f"{base_file_path}.{ext}"
        if os.path.exists(path):
            logger.debug(f"Found an already existing file: '{base_file_path}'")
            return path
    return None

def save_file(file: FileStorage, file_path: os.PathLike) -> bool:
    """Save the file to the specified path."""
    try:
        file.save(file_path)
        logger.info(f"File saved successfully: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving file '{file_path}': {e}")
        return False

def remove_file(file_path: os.PathLike) -> bool:
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