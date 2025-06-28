from app.models.storyslide import StorySlide
from app.models.nightline import Nightline
from app.models.nightlinestatus import NightlineStatus
from app.config import Config

from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

from werkzeug.datastructures import FileStorage
from io import BytesIO
import tempfile
from pathlib import Path


sample_jpg = FileStorage(stream=BytesIO(b"fake jpg content"), filename="example.jpg", content_type="image/jpg")
sample_noextension = FileStorage(stream=BytesIO(b"missing extension"), filename="example", content_type="image/jpeg")

# -------------------------
# _save_story_slide_file
# -------------------------
def test__save_story_slide_file_validate_file_extension_fails():
    nightline = Nightline.add_nightline("storyslide_line")
    nightlinestatus = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    assert StorySlide._save_story_slide_file(sample_noextension, nightlinestatus) is None

@patch("app.models.storyslide.ensure_storage_path_exists")
def test__save_story_slide_file_validate_storage_path_fails(mock_ensure_storage_path_exists):
    mock_ensure_storage_path_exists.return_value = False
    
    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    assert StorySlide._save_story_slide_file(sample_jpg, nightline_status) is None

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.ensure_storage_path_exists")
@patch("app.models.storyslide.check_file_already_exists")
def test__save_story_slide_file_story_slide_already_exists_overwrite_false(mock_check_file_already_exists, mock_ensure_storage_path_exists, mock_logger):
    mock_ensure_storage_path_exists.return_value = True
    mock_check_file_already_exists.return_value = "./fake/existing/path"

    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    assert StorySlide._save_story_slide_file(sample_jpg, nightline_status, overwrite=False) is None

    mock_logger.warning.assert_called_once_with(f"Found an existing story slide for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}'")

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.ensure_storage_path_exists")
@patch("app.models.storyslide.check_file_already_exists")
@patch("app.models.storyslide.save_file")
def test__save_story_slide_file_story_slide_already_exists_overwrite_true_save_fails(mock_save_file, mock_check_file_already_exists, mock_ensure_storage_path_exists, mock_logger):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
        tmp.write(b"\xff\xd8\xff\xe0" + b"JPEG TEST")
        tmp_path = Path(tmp.name)

        mock_ensure_storage_path_exists.return_value = True
        mock_check_file_already_exists.return_value = tmp_path
        mock_save_file.return_value = False

        nightline = Nightline.get_nightline("storyslide_line")
        nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

        assert StorySlide._save_story_slide_file(sample_jpg, nightline_status, overwrite=True) is None

        mock_logger.debug.assert_called_once_with(f"Replacing the already existing story slide: '{tmp_path}' for status: '{nightline_status.status.name}'")

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.ensure_storage_path_exists")
@patch("app.models.storyslide.check_file_already_exists")
@patch("app.models.storyslide.save_file")
def test__save_story_slide_file_story_slide_already_exists_overwrite_true_successfully(mock_save_file, mock_check_file_already_exists, mock_ensure_storage_path_exists, mock_logger):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
        tmp.write(b"\xff\xd8\xff\xe0" + b"JPEG TEST")
        tmp_path = Path(tmp.name)

        mock_ensure_storage_path_exists.return_value = True
        mock_check_file_already_exists.return_value = tmp_path
        mock_save_file.return_value = True

        nightline = Nightline.get_nightline("storyslide_line")
        nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

        return_path = Path(Config.UPLOAD_FOLDER, nightline_status.nightline.name, nightline.status.name + ".jpg")

        assert StorySlide._save_story_slide_file(sample_jpg, nightline_status, overwrite=True) == return_path

        mock_logger.debug.assert_called_once_with(f"Replacing the already existing story slide: '{tmp_path}' for status: '{nightline_status.status.name}'")

        StorySlide.remove_story_slide(nightline_status)

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.ensure_storage_path_exists")
@patch("app.models.storyslide.check_file_already_exists")
@patch("app.models.storyslide.save_file")
def test__save_story_slide_file_successfully(mock_save_file, mock_check_file_already_exists, mock_ensure_storage_path_exists, mock_logger):
    mock_ensure_storage_path_exists.return_value = True
    mock_check_file_already_exists.return_value = None
    mock_save_file.return_value = True

    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    return_path = Path(Config.UPLOAD_FOLDER, nightline_status.nightline.name, nightline.status.name + ".jpg")

    assert StorySlide._save_story_slide_file(sample_jpg, nightline_status, overwrite=True) == return_path


# -------------------------
# get_story_slide_by_nightline_status
# -------------------------
@patch("app.models.storyslide.logger")
def test_get_story_slide_by_nightline_status_no_story_slide(mock_logger):
    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    assert StorySlide.get_story_slide_by_nightline_status(nightline_status) is None

    mock_logger.debug.assert_called_once_with(f"Fetching story slide for nightline status with ID: '{nightline_status.id}'")
    mock_logger.info.assert_called_once_with(f"Story Slide for nightline status '{nightline_status.status.name}' of nightline '{nightline_status.nightline.name}' not found")

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.StorySlide._save_story_slide_file")
def test_get_story_slide_by_nightline_status_successfully(mock__save_story_slide_file, mock_logger):
    mock__save_story_slide_file.return_value = Path("./fake/path")
    
    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    story_slide = StorySlide.update_story_slide(sample_jpg, nightline_status)

    assert StorySlide.get_story_slide_by_nightline_status(nightline_status) == story_slide

    mock_logger.debug.assert_any_call(f"Fetching story slide for nightline status with ID: '{nightline_status.id}'")
    mock_logger.debug.assert_any_call(f"Found story slide for status '{nightline_status.status.name}' of nightline '{nightline_status.nightline.name}'")


# -------------------------
# update_story_slide
# -------------------------
@patch("app.models.storyslide.StorySlide._save_story_slide_file")
def test_update_story_slide_saving_fails(mock__save_story_slide_file):
    mock__save_story_slide_file.return_value = None
    
    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    assert StorySlide.update_story_slide(sample_jpg, nightline_status) is None

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.StorySlide._save_story_slide_file")
def test_update_story_slide_update_existing_successfully(mock__save_story_slide_file, mock_logger):
    mock__save_story_slide_file.return_value = "./fake/path"
    
    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    assert isinstance(StorySlide.update_story_slide(sample_jpg, nightline_status), StorySlide)

    mock_logger.info.assert_called_once_with(f"StorySlide for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}' updated successfully")

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.StorySlide._save_story_slide_file")
@patch("app.models.storyslide.db.session.commit")
def test_update_story_slide_database_error(mock_commit, mock__save_story_slide_file, mock_logger):
    mock__save_story_slide_file.return_value = "./fake/path"
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    assert StorySlide.update_story_slide(sample_jpg, nightline_status) is None

    mock_logger.error.assert_called_once_with(f"Error creating StorySlide for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}': Database error")

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.StorySlide._save_story_slide_file")
def test_update_story_slide_create_new_successfully(mock__save_story_slide_file, mock_logger):
    mock__save_story_slide_file.return_value = "./fake/path"
    
    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)
    StorySlide.remove_story_slide(nightline_status)

    assert isinstance(StorySlide.update_story_slide(sample_jpg, nightline_status), StorySlide)

    mock_logger.info.assert_called_once_with(f"StorySlide for status: '{nightline_status.status.name}' of nightline: '{nightline_status.nightline.name}' updated successfully")


# -------------------------
# remove_story_slide
# -------------------------
@patch("app.models.storyslide.logger")
def test_remove_story_slide_failed_to_remove_file(mock_logger):
    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)

    assert StorySlide.remove_story_slide(nightline_status) is False

    mock_logger.warning.assert_called_once_with(f"Failed to remove file at path: '{nightline_status.instagram_story_slide.path}' for status: '{nightline.status.name}' of nightline: '{nightline.name}'")

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.db.session.commit")
@patch("app.models.storyslide.remove_file")
def test_remove_story_slide_database_error(mock_remove_file, mock_commit, mock_logger):
    mock_remove_file.return_value = True
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)
    
    assert StorySlide.remove_story_slide(nightline_status) is False

    mock_logger.error.assert_called_once_with(f"Error removing StorySlide from DB for status: '{nightline.status.name}' of nightline: '{nightline.name}': Database error")

@patch("app.models.storyslide.logger")
@patch("app.models.storyslide.remove_file")
def test_remove_story_slide_successfully(mock_remove_file, mock_logger):
    mock_remove_file.return_value = True

    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)
    
    assert StorySlide.remove_story_slide(nightline_status) is True

    mock_logger.info.assert_called_once_with(f"StorySlide for status: '{nightline.status.name}' of nightline: '{nightline.name}' removed successfully")

@patch("app.models.storyslide.logger")
def test_remove_story_slide_no_story_slide_found(mock_logger):
    nightline = Nightline.get_nightline("storyslide_line")
    nightline_status = NightlineStatus.get_nightline_status(nightline.id, nightline.status.id)
    
    assert StorySlide.remove_story_slide(nightline_status) is False

    mock_logger.warning.assert_called_once_with(f"No story slide found for status: '{nightline.status.name}' of nightline: '{nightline.name}'")
