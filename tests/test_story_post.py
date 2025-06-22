from unittest.mock import MagicMock, patch

import pytest
from instagrapi.exceptions import LoginRequired

from app.story_post import delete_story_by_id, login_user, post_story


@pytest.fixture
def mock_client():
    return MagicMock()


# -------------------------
# login_user
# -------------------------
def test_login_user_with_valid_session(mock_client):
    mock_client.load_settings.return_value = {"uuids": "some-uuid"}
    mock_client.get_timeline_feed.return_value = {}

    with patch("os.path.exists", return_value=True):
        assert login_user(mock_client, "user", "pass") is True

    mock_client.load_settings.assert_called_once_with("session.json")
    mock_client.set_settings.assert_called()
    mock_client.login.assert_called()
    mock_client.get_timeline_feed.assert_called()


@patch("app.story_post.logger")
def test_login_user_with_invalid_session_then_successful_password_login(mock_logger, mock_client):
    mock_client.load_settings.return_value = {"uuids": "some-uuid"}
    mock_client.get_settings.return_value = {"uuids": "some-uuid"}
    mock_client.get_timeline_feed.side_effect = [LoginRequired, {}]

    with patch("os.path.exists", return_value=True):
        assert login_user(mock_client, "user", "pass") is True

    assert mock_client.login.call_count == 2
    mock_logger.info.assert_any_call("Session is invalid, need to login via username and password")


@patch("app.story_post.logger")
def test_login_user_with_session_exception_then_successful_password_login(mock_logger, mock_client):
    mock_client.load_settings.return_value = {"uuids": "some-uuid"}
    mock_client.get_timeline_feed.side_effect = Exception("session error")

    mock_client.login.return_value = True
    mock_client.dump_settings.return_value = None

    with patch("os.path.exists", return_value=True):
        assert login_user(mock_client, "user", "pass") is True

    mock_client.load_settings.assert_called_once_with("session.json")
    mock_client.set_settings.assert_called()
    assert mock_client.login.call_count == 2
    mock_client.get_timeline_feed.assert_called()

    assert mock_logger.info.call_count == 2
    mock_logger.info.assert_any_call("Couldn't login user using session information: %s" % mock_client.get_timeline_feed.side_effect)
    mock_logger.info.assert_any_call("Attempting to login via username and password. username: %s" % "user")


@patch("app.story_post.logger")
def test_login_user_without_session_then_password_login_fails(mock_logger, mock_client):
    mock_client.login.return_value = False

    with patch("os.path.exists", return_value=False):
        assert login_user(mock_client, "user", "pass") is False

    assert mock_client.login.call_count == 1

    assert mock_logger.info.call_count == 1
    mock_logger.info.assert_any_call("Attempting to login via username and password. username: %s" % "user")


@patch("app.story_post.logger")
def test_login_user_without_session_then_exception_in_password_login(mock_logger, mock_client):
    mock_client.login.side_effect = Exception("session error")

    with patch("os.path.exists", return_value=False):
        assert login_user(mock_client, "user", "pass") is False

    assert mock_client.login.call_count == 1

    assert mock_logger.info.call_count == 2
    mock_logger.info.assert_any_call("Attempting to login via username and password. username: %s" % "user")
    mock_logger.info.assert_any_call("Couldn't login user using username and password: %s" % mock_client.login.side_effect)


from pathlib import Path

# -------------------------
# post_story
# -------------------------
from unittest.mock import MagicMock, patch

from app.story_post import post_story  # or wherever it's located


@patch("app.story_post.Client")
@patch("app.story_post.logger")
def test_post_story_successful(mock_logger, mock_client_cls):
    # Create mock Client instance
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    # Simulate image upload success
    mock_client.photo_upload_to_story.return_value.pk = "media123"

    image_path = Path("/fake/image.jpg")
    username = "user"
    password = "pass"

    # Patch login_user and os.path.exists
    with patch("app.story_post.login_user", return_value=True) as mock_login_user, patch("os.path.exists", return_value=True):
        assert post_story(image_path, username, password) == "media123"

    mock_login_user.assert_called_once_with(mock_client, username, password)
    mock_client.photo_upload_to_story.assert_called_once_with(image_path)
    mock_logger.info.assert_called_with(f"Story {image_path} with ID: media123, posted successfully.")


@patch("app.story_post.Client")
@patch("app.story_post.logger")
def test_post_story_login_user_failed(mock_logger, mock_client_cls):
    # Create mock Client instance
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    image_path = Path("/fake/image.jpg")
    username = "user"
    password = "pass"

    # Patch login_user and os.path.exists
    with patch("app.story_post.login_user", return_value=False) as mock_login_user:
        assert post_story(image_path, username, password) is None

    mock_login_user.assert_called_once_with(mock_client, username, password)


@patch("app.story_post.Client")
@patch("app.story_post.logger")
def test_post_story_image_path_does_not_exist(mock_logger, mock_client_cls):
    # Create mock Client instance
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    image_path = Path("/non/existing/image.jpg")
    username = "user"
    password = "pass"

    # Patch login_user and os.path.exists
    with patch("app.story_post.login_user", return_value=True) as mock_login_user, patch("os.path.exists", return_value=False):

        assert post_story(image_path, username, password) is None

    mock_login_user.assert_called_once_with(mock_client, username, password)
    mock_logger.error.assert_called_with(f"Image not found: {image_path}")


@patch("app.story_post.Client")
@patch("app.story_post.logger")
def test_post_story_exception_on_upload(mock_logger, mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    # Simulate image upload success
    mock_client.photo_upload_to_story.side_effect = Exception("upload error")

    image_path = Path("/fake/image.jpg")
    username = "user"
    password = "pass"

    # Patch login_user and os.path.exists
    with patch("app.story_post.login_user", return_value=True) as mock_login_user, patch("os.path.exists", return_value=True):
        assert post_story(image_path, username, password) is None

    mock_login_user.assert_called_once_with(mock_client, username, password)
    mock_client.photo_upload_to_story.assert_called_once_with(image_path)
    mock_logger.error.assert_called_with(f"Failed to post story: upload error")


# -------------------------
# delete_story
# -------------------------
@patch("app.story_post.Client")
@patch("app.story_post.logger")
def test_delete_story_by_id_success(mock_logger, mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.media_delete.return_value = None  # success

    with patch("app.story_post.login_user", return_value=True) as mock_login_user:
        assert delete_story_by_id("12345", "user", "pass") is True

    mock_login_user.assert_called_once_with(mock_client, "user", "pass")
    mock_client.media_delete.assert_called_once_with("12345")
    mock_logger.info.assert_called_once_with("Story with ID 12345 deleted successfully.")


@patch("app.story_post.Client")
@patch("app.story_post.logger")
def test_delete_story_by_id_login_fails(mock_logger, mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    with patch("app.story_post.login_user", return_value=False) as mock_login_user:
        assert delete_story_by_id("12345", "user", "pass") is False

    mock_login_user.assert_called_once_with(mock_client, "user", "pass")
    mock_client.media_delete.assert_not_called()
    mock_logger.info.assert_not_called()
    mock_logger.error.assert_not_called()


@patch("app.story_post.Client")
@patch("app.story_post.logger")
def test_delete_story_by_id_exception(mock_logger, mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.media_delete.side_effect = Exception("something went wrong")

    with patch("app.story_post.login_user", return_value=True) as mock_login_user:
        assert delete_story_by_id("12345", "user", "pass") is False

    mock_login_user.assert_called_once_with(mock_client, "user", "pass")
    mock_client.media_delete.assert_called_once_with("12345")
    mock_logger.error.assert_called_once_with("Failed to delete story with ID 12345: something went wrong")
