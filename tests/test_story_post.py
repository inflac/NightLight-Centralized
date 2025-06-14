import pytest
from unittest.mock import patch, MagicMock, mock_open
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

from app.story_post import login_user


@pytest.fixture
def mock_client():
    return MagicMock()

@patch("app.story_post.logger")
def test_login_with_valid_session(mock_logger, mock_client):
    mock_client.load_settings.return_value = {"uuids": "some-uuid"}
    mock_client.get_timeline_feed.return_value = {}

    with patch("os.path.exists", return_value=True):
        assert login_user(mock_client, "user", "pass") is True

    mock_client.load_settings.assert_called_once_with("session.json")
    mock_client.set_settings.assert_called()
    mock_client.login.assert_called()
    mock_client.get_timeline_feed.assert_called()

@patch("app.story_post.logger")
def test_login_with_invalid_session_then_successful_password_login(mock_logger, mock_client):
    mock_client.load_settings.return_value = {"uuids": "some-uuid"}
    mock_client.get_settings.return_value = {"uuids": "some-uuid"}
    mock_client.get_timeline_feed.side_effect = [LoginRequired, {}]

    with patch("os.path.exists", return_value=True):
        assert login_user(mock_client, "user", "pass") is True

    assert mock_client.login.call_count == 2
    mock_logger.info.assert_any_call("Session is invalid, need to login via username and password")
