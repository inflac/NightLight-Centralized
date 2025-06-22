import os
import shutil
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from werkzeug.datastructures import FileStorage

from app.filehandler import (
    check_file_already_exists,
    ensure_storage_path_exists,
    remove_file,
    save_file,
    validate_file_extension,
)

sample_jpg = FileStorage(stream=BytesIO(b"fake jpg content"), filename="example.jpg", content_type="image/jpg")
sample_png = FileStorage(stream=BytesIO(b"fake png content"), filename="example.PNG", content_type="image/png")
sample_jpeg = FileStorage(stream=BytesIO(b"fake jpeg content"), filename="example.jpeg", content_type="image/jpeg")
sample_gif = FileStorage(stream=BytesIO(b"fake gif content"), filename="example.GIF", content_type="image/gif")
sample_mp4 = FileStorage(stream=BytesIO(b"fake mp4 content"), filename="example.mp4", content_type="video/mp4")
sample_txt = FileStorage(stream=BytesIO(b"fake txt content"), filename="example.txt", content_type="text/plain")
sample_noextension = FileStorage(stream=BytesIO(b"missing extension"), filename="example", content_type="image/jpeg")
sample_empty = FileStorage(stream=BytesIO(b""), filename="", content_type="application/octet-stream")


# -------------------------
# validate_file_extension
# -------------------------
@pytest.mark.parametrize(
    "file,expected",
    [
        (sample_jpg, "jpg"),
        (sample_png, "png"),
        (sample_jpeg, "jpeg"),
        (sample_gif, None),
        (sample_mp4, None),
        (sample_txt, None),
        (sample_noextension, None),
        (sample_empty, None),
        (None, None),
    ],
)
def test_validate_file_extension(file, expected):
    assert validate_file_extension(file) == expected


# -------------------------
# ensure_storage_path_exists
# -------------------------
def test_ensure_storage_path_exists_creates_directory():
    temp_dir = tempfile.mkdtemp()
    test_path = Path(temp_dir) / "new_folder"

    # Make sure the directory does not exist before
    assert not test_path.exists()

    # Should create the directory
    result = ensure_storage_path_exists(test_path)
    assert result is True
    assert test_path.exists()
    assert test_path.is_dir()

    shutil.rmtree(temp_dir)  # cleanup


def test_ensure_storage_path_exists_existing_directory():
    with tempfile.TemporaryDirectory() as existing_dir:
        path = Path(existing_dir)

        # Directory already exists
        assert path.exists()

        result = ensure_storage_path_exists(path)
        assert result is True
        assert path.exists()  # still exists


@patch("app.filehandler.logger")
def test_ensure_storage_path_exists_failure(mock_logger, monkeypatch):
    # Simulate a failure in os.makedirs
    def raise_oserror(path, exist_ok=False):
        raise OSError("Simulated permission error")

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "fail_here"

        monkeypatch.setattr(os, "makedirs", raise_oserror)

        result = ensure_storage_path_exists(path)
        assert result is False
        assert not path.exists()
        mock_logger.error.assert_called_with(f"Error creating storage directory '{path}': Simulated permission error")


# -------------------------
# check_file_already_exists
# -------------------------
def test_check_file_already_exists_allowed_file_extension():
    temp_dir = tempfile.mkdtemp()
    fd, path_str = tempfile.mkstemp(dir=temp_dir, suffix=".png")
    os.close(fd)
    base_path = Path(path_str).with_suffix("")

    assert check_file_already_exists(base_path).resolve() == Path(path_str).resolve()

    shutil.rmtree(temp_dir)


def test_check_file_already_exists_unallowed_file_extension():
    temp_dir = tempfile.mkdtemp()
    fd, path_str = tempfile.mkstemp(dir=temp_dir, suffix=".txt")
    os.close(fd)
    base_path = Path(path_str).with_suffix("")

    assert check_file_already_exists(base_path) == None

    shutil.rmtree(temp_dir)


# -------------------------
# save_file
# -------------------------
@patch("app.filehandler.logger")
def test_save_file_successfull(mock_logger):
    temp_dir = tempfile.mkdtemp()
    temp_file_path = Path(temp_dir, sample_jpg.filename)

    assert save_file(sample_jpg, temp_file_path) == True
    mock_logger.info.assert_called_with(f"File saved successfully: {temp_file_path}")

    shutil.rmtree(temp_dir)


@patch("app.filehandler.logger")
def test_save_file_exception(mock_logger):
    temp_dir = tempfile.mkdtemp()
    temp_file_path = Path(temp_dir, sample_jpg.filename)

    # Patch den save-Methoden-Pfad korrekt
    with patch("werkzeug.datastructures.FileStorage.save") as mock_save:
        mock_save.side_effect = OSError("Simulated permission error")

        assert save_file(sample_jpg, temp_file_path) == False
        mock_logger.error.assert_called_with(f"Error saving file '{temp_file_path}': Simulated permission error")

    shutil.rmtree(temp_dir)


# -------------------------
# remove_file
# -------------------------
@patch("app.filehandler.logger")
def test_remove_file_path_do_not_exist(mock_logger):
    nonexistent_path = Path("/this/path/definitely/does/not/exist.xyz")
    assert remove_file(nonexistent_path) == False
    mock_logger.warning.assert_called_with(f"File '{nonexistent_path}' does not exist")


@patch("app.filehandler.logger")
def test_remove_file_path_do_exsit(mock_logger):
    temp_dir = tempfile.mkdtemp()
    fd, temp_file_path = tempfile.mkstemp(dir=temp_dir, suffix=".png")
    os.close(fd)

    assert remove_file(temp_file_path) == True
    mock_logger.info.assert_called_with(f"File '{temp_file_path}' removed successfully")

    shutil.rmtree(temp_dir)


@patch("app.filehandler.logger")
def test_remove_file_exception(mock_logger):
    temp_dir = tempfile.mkdtemp()
    fd, temp_file_path = tempfile.mkstemp(dir=temp_dir, suffix=".png")
    os.close(fd)

    with patch("os.remove") as mock_remove:
        mock_remove.side_effect = OSError("Simulated permission error")

        assert remove_file(Path(temp_file_path)) == False
        mock_logger.error.assert_called_with(f"Error removing file '{temp_file_path}': Simulated permission error")

    shutil.rmtree(temp_dir)
