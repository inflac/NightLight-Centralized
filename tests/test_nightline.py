from unittest.mock import MagicMock, patch

from sqlalchemy.exc import SQLAlchemyError

from app.models.apikey import ApiKey
from app.models.nightline import Nightline
from app.models.nightlinestatus import NightlineStatus
from app.models.status import Status


# -------------------------
# get_nightline
# -------------------------
@patch("app.models.nightline.logger")
@patch("app.models.nightline.Nightline.query")
def test_get_nightline_found(mock_query, mock_logger):
    # Arrange
    mock_nightline = MagicMock()
    mock_query.filter_by.return_value.first.return_value = mock_nightline

    # Act
    assert Nightline.get_nightline("testline") == mock_nightline

    mock_logger.debug.assert_any_call("Fetching nightline by name: 'testline'")
    mock_logger.debug.assert_any_call("Found nightline: 'testline'")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.Nightline.query")
def test_get_nightline_not_found(mock_query, mock_logger):
    mock_query.filter_by.return_value.first.return_value = None

    assert Nightline.get_nightline("ghostline") is None

    mock_logger.debug.assert_called_once_with("Fetching nightline by name: 'ghostline'")
    mock_logger.info.assert_called_once_with("Nightline 'ghostline' not found")


# -------------------------
# add_nightline
# -------------------------
@patch("app.models.nightline.logger")
@patch("app.models.status.Status.get_status")
def test_add_nightline_missing_default_status(mock_get_status, mock_logger):
    mock_get_status.return_value = None

    assert Nightline.add_nightline("morningline") is None

    mock_logger.error.assert_called_with(f"Nightline was not added because the default status is missing")


@patch("app.models.nightline.logger")
def test_add_nightline_successfull(mock_logger):
    nightline = Nightline.add_nightline("morningline")
    assert isinstance(nightline, Nightline)
    assert nightline.name == "morningline"

    mock_logger.debug.assert_any_call(f"Adding new nightline: '{nightline.name}'")
    mock_logger.debug.assert_any_call(f"Created nightline: '{nightline.name}'")
    mock_logger.debug.assert_any_call(f"Created API-Key for nightline: '{nightline.name}'")
    mock_logger.info.assert_called_once_with(f"Nightline '{nightline.name}' added successfully")


@patch("app.models.nightline.logger")
@patch("app.models.instagram.db.session.commit")
def test_add_nightline_exception(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("DB error")

    assert Nightline.add_nightline("morningline") is None

    mock_logger.error.assert_called_once_with(f"Error adding nightline 'morningline': DB error")


# -------------------------
# remove_nightline
# -------------------------
@patch("app.models.nightline.logger")
def test_remove_nightline_successful(mock_logger):  # Remove previously created 'morningline'
    nightline = Nightline.remove_nightline("morningline")
    assert isinstance(nightline, Nightline)
    assert nightline.name == "morningline"

    mock_logger.debug.assert_any_call(f"Removing nightline: 'morningline'")
    mock_logger.debug.assert_any_call(f"Removed api key for nightline: 'morningline'")
    mock_logger.info.assert_called_once_with(f"Nightline 'morningline' removed successfully")


@patch("app.models.nightline.logger")
def test_remove_nightline_no_nightline_found(mock_logger):
    assert Nightline.remove_nightline("ghostline") is None

    mock_logger.debug.assert_any_call(f"Removing nightline: 'ghostline'")
    mock_logger.info.assert_any_call(f"Nightline 'ghostline' not found, nothing to remove")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.Nightline.get_nightline")
@patch("app.models.apikey.ApiKey.get_api_key")
def test_remove_nightline_no_api_key_found(mock_get_api_key, mock_get_nightline, mock_logger):
    mock_get_nightline.return_value = Nightline(id=123)
    mock_get_api_key.return_value = None

    assert Nightline.remove_nightline("nokeyline") is None

    mock_logger.debug.assert_called_once_with(f"Removing nightline: 'nokeyline'")
    mock_logger.warning.assert_called_once_with(f"Api key for nightline 'nokeyline' not found, can't remove the nightline")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.db.session.delete")
def test_remove_nightline_exception(mock_delete, mock_logger):
    mock_delete.side_effect = Exception("Wierd exception occured")
    Nightline.add_nightline("templine")

    assert Nightline.remove_nightline("templine") is None

    mock_logger.debug.assert_any_call(f"Removing nightline: 'templine'")
    mock_logger.error.assert_called_once_with(f"Error removing nightline 'templine': Wierd exception occured")


# -------------------------
# list_nightlines
# -------------------------
@patch("app.models.nightline.logger")
def test_list_nightlines_no_filters(mock_logger):
    templine = Nightline.get_nightline("templine")
    Testline = Nightline.get_nightline("Testline")

    assert Nightline.list_nightlines() == [Testline, templine]

    mock_logger.debug.assert_any_call("Listing all nightlines with filters")
    mock_logger.info.assert_any_call(f"Listed 2 nightlines")

    Nightline.remove_nightline("Testline")


@patch("app.models.nightline.logger")
def test_list_nightlines_canceled_filter(mock_logger):
    templine = Nightline.get_nightline("templine")
    templine.set_status("canceled")

    assert Nightline.list_nightlines(status_filter="canceled") == [templine]

    mock_logger.debug.assert_any_call("Listing all nightlines with filters")
    mock_logger.info.assert_any_call(f"Listed 1 nightlines")


@patch("app.models.nightline.logger")
def test_list_nightlines_language_filter_english(mock_logger):
    templine = Nightline.get_nightline("templine")
    templine.set_status("english")

    assert Nightline.list_nightlines(language_filter="en") == [templine]

    mock_logger.debug.assert_any_call("Listing all nightlines with filters")
    mock_logger.info.assert_any_call(f"Listed 1 nightlines")


@patch("app.models.nightline.logger")
def test_list_nightlines_language_filter_german(mock_logger):
    templine = Nightline.get_nightline("templine")
    templine.set_status("german")

    assert Nightline.list_nightlines(language_filter="de") == [templine]

    mock_logger.debug.assert_any_call("Listing all nightlines with filters")
    mock_logger.info.assert_any_call(f"Listed 1 nightlines")


@patch("app.models.nightline.logger")
def test_list_nightlines_language_unknown_and_now_filter(mock_logger):
    assert Nightline.list_nightlines(language_filter="python", now_filter=True) == []

    mock_logger.debug.assert_any_call("Listing all nightlines with filters")
    mock_logger.info.assert_any_call(f"Listed 0 nightlines")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.Nightline.query")
def test_list_nightlines_exception(mock_query, mock_logger):
    mock_query.join.side_effect = Exception("Unknown error")

    assert Nightline.list_nightlines() == []

    mock_logger.debug.assert_any_call("Listing all nightlines with filters")
    mock_logger.error.assert_called_once_with("Error while fetching the nightlines: Unknown error")


# -------------------------
# set_status
# -------------------------
@patch("app.models.nightline.logger")
def test_set_status_successfull(mock_logger):
    nightline = Nightline.get_nightline("templine")
    assert nightline.set_status("english") is True

    mock_logger.debug.assert_any_call(f"Set status of nightline '{nightline.name}' to: 'english'")
    mock_logger.info.assert_called_once_with(f"Status 'english' set successfully")


@patch("app.models.nightline.logger")
def test_set_status_no_valid_status(mock_logger):
    nightline = Nightline.get_nightline("templine")
    assert nightline.set_status("bsod") is False

    mock_logger.debug.assert_any_call(f"Set status of nightline '{nightline.name}' to: 'bsod'")


@patch("app.models.nightline.logger")
@patch("app.models.status.Status.get_status")
def test_set_status_exception(mock_get_status, mock_logger):
    mock_get_status.side_effect = Exception("Unknown Error")

    nightline = Nightline.get_nightline("templine")
    assert nightline.set_status("bsod") is False

    mock_logger.debug.assert_any_call(f"Set status of nightline '{nightline.name}' to: 'bsod'")
    mock_logger.error.assert_called_once_with(f"Failed to set status 'bsod' for nightline '{nightline.name}': Unknown Error")


# -------------------------
# reset_status
# -------------------------
@patch("app.models.nightline.logger")
def test_reset_status_successfull(mock_logger):
    nightline = Nightline.get_nightline("templine")

    assert nightline.reset_status() is True

    mock_logger.info.assert_any_call(f"Reset the status of nightline: '{nightline.name}'")


# -------------------------
# set_now
# -------------------------
@patch("app.models.nightline.logger")
def test_set_now_successfull(mock_logger):
    nightline = Nightline.get_nightline("templine")

    assert nightline.set_now(True) is True

    mock_logger.info.assert_called_once_with(f"Set the now value of nightline: '{nightline.name}' to: 'True'")


@patch("app.models.nightline.logger")
@patch("app.models.instagram.db.session.commit")
def test_set_now_exception(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("DB error")

    nightline = Nightline.get_nightline("templine")
    assert nightline.set_now(True) is False

    mock_logger.info.assert_called_once_with(f"Set the now value of nightline: '{nightline.name}' to: 'True'")
    mock_logger.error.assert_called_once_with(f"Failed to set now value for nightline '{nightline.name}' to 'True': DB error")


# -------------------------
# get_instagram_story_config
# -------------------------
def test_get_instagram_story_config_story_false():
    nightline = Nightline.get_nightline("templine")
    nightline.set_status("technical-issues")

    assert nightline.get_instagram_story_config() is False


def test_get_instagram_story_config_story_true():
    nightline = Nightline.get_nightline("templine")
    NightlineStatus.update_instagram_story(nightline, nightline.status, True)

    assert nightline.get_instagram_story_config() is True


@patch("app.models.nightline.NightlineStatus.get_nightline_status")
def test_get_instagram_story_config_story_nightline_status_none(mock_get_nightline_status):
    mock_get_nightline_status.return_value = None
    nightline = Nightline.get_nightline("templine")

    assert nightline.get_instagram_story_config() is False


# -------------------------
# set_instagram_media_id
# -------------------------
@patch("app.models.nightline.logger")
def test_set_instagram_media_id_successful(mock_logger):
    nightline = Nightline.get_nightline("templine")
    old_media_id = nightline.instagram_media_id

    assert nightline.set_instagram_media_id("testID") is True
    assert nightline.instagram_media_id != old_media_id

    mock_logger.debug.assert_any_call(f"Setting media id for a status of nightline '{nightline.name}'")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.db.session.commit")
def test_set_instagram_media_id_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("templine")
    old_media_id = nightline.instagram_media_id

    assert nightline.set_instagram_media_id("testID") is False
    assert nightline.instagram_media_id == old_media_id

    mock_logger.debug.assert_any_call(f"Setting media id for a status of nightline '{nightline.name}'")
    mock_logger.error.assert_called_once_with(f"Database error while setting Instagram media id for nightline '{nightline.name}': Database error")


# -------------------------
# get_api_key
# -------------------------
def test_get_api_key():
    nightline = Nightline.get_nightline("templine")
    api_key = nightline.get_api_key()
    assert isinstance(api_key, ApiKey)


# -------------------------
# renew_api_key
# -------------------------
@patch("app.models.nightline.logger")
def test_renew_api_key_successfull(mock_logger):
    nightline = Nightline.get_nightline("templine")
    old_api_key = nightline.get_api_key().key

    assert nightline.renew_api_key() is True
    assert nightline.get_api_key().key != old_api_key

    mock_logger.debug.assert_any_call(f"Renew api key of nightline: '{nightline.name}'")
    mock_logger.info.assert_called_once_with(f"API key for nightline '{nightline.name}' renewed successfully")


@patch("app.models.nightline.logger")
@patch("app.models.apikey.ApiKey.get_api_key")
def test_renew_api_key_no_api_key_found(mock_get_api_key, mock_logger):
    mock_get_api_key.return_value = None

    nightline = Nightline.get_nightline("templine")

    assert nightline.renew_api_key() is False

    mock_logger.debug.assert_any_call(f"Renew api key of nightline: '{nightline.name}'")
    mock_logger.warning.assert_called_once_with(f"No API key found for nightline: '{nightline.name}'")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.db.session.commit")
def test_renew_api_key_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("templine")

    assert nightline.renew_api_key() is False

    mock_logger.debug.assert_any_call(f"Renew api key of nightline: '{nightline.name}'")
    mock_logger.error.assert_called_once_with(f"Database error while renewing API key for nightline '{nightline.name}': Database error")


# -------------------------
# add_instagram_account
# -------------------------
@patch("app.models.nightline.logger")
@patch("app.models.nightline.db.session.commit")
def test_add_instagram_account_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("templine")

    username = "test_user"
    password = "test_pass"

    assert nightline.add_instagram_account(username, password) is False

    mock_logger.error.assert_called_once_with(f"Database error while adding Instagram account for nightline '{nightline.name}': Database error")


@patch("app.models.nightline.logger")
def test_add_instagram_account_successfull(mock_logger):
    nightline = Nightline.get_nightline("templine")

    username = "test_user"
    password = "test_pass"

    assert nightline.add_instagram_account(username, password) is True

    mock_logger.info.assert_called_once_with(f"Instagram account added for nightline '{nightline.name}' with username '{username}'")


@patch("app.models.nightline.logger")
def test_add_instagram_account_already_exists(mock_logger):
    nightline = Nightline.get_nightline("templine")

    username = "test_user"
    password = "test_pass"

    assert nightline.add_instagram_account(username, password) is False

    mock_logger.warning.assert_called_once_with(f"Instagram account already exists for nightline '{nightline.name}'")


# -------------------------
# update_instagram_username
# -------------------------
@patch("app.models.nightline.logger")
def test_update_instagram_username_successfull(mock_logger):
    nightline = Nightline.get_nightline("templine")
    old_username = nightline.instagram_account.username

    new_username = "new_user123"
    assert nightline.update_instagram_username(new_username) is True

    assert old_username != new_username

    mock_logger.info.assert_called_once_with(f"Instagram username updated to '{new_username}' for Nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.db.session.commit")
def test_update_instagram_username_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("templine")

    assert nightline.update_instagram_username("new_username") is False

    mock_logger.error.assert_called_once_with(f"Database error while updating username of Instagram account for nightline '{nightline.name}': Database error")


@patch("app.models.nightline.logger")
def test_update_instagram_username_no_instagram_acc_added(mock_logger):
    nightline = Nightline.get_nightline("templine")
    nightline.delete_instagram_account()

    assert nightline.update_instagram_username("new_user123") is False

    mock_logger.warning.assert_called_once_with(f"No Instagram account configured for nightline '{nightline.name}'.")


# -------------------------
# update_instagram_password
# -------------------------
@patch("app.models.nightline.logger")
def test_update_instagram_password_no_instagram_acc_added(mock_logger):
    nightline = Nightline.get_nightline("templine")

    assert nightline.update_instagram_password("new_pass123") is False

    mock_logger.warning.assert_called_once_with(f"No Instagram account configured for nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
def test_update_instagram_password_successfull(mock_logger):
    nightline = Nightline.get_nightline("templine")
    nightline.add_instagram_account("user", "pass")
    old_password = nightline.instagram_account.get_password()

    new_password = "new_pass123"
    assert nightline.update_instagram_password(new_password) is True

    assert old_password != new_password

    mock_logger.info.assert_any_call(f"Instagram password updated for Nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.db.session.commit")
def test_update_instagram_password_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("templine")

    assert nightline.update_instagram_password("new_pass123") is False

    mock_logger.error.assert_called_once_with(f"Database error while updating password of Instagram account for nightline '{nightline.name}': Database error")


# -------------------------
# delete_instagram_account
# -------------------------
@patch("app.models.nightline.logger")
@patch("app.models.nightline.db.session.commit")
def test_delete_instagram_account_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("templine")

    assert nightline.delete_instagram_account() is False

    mock_logger.error.assert_called_once_with(f"Database error while deleting Instagram account of nightline '{nightline.name}': Database error")


@patch("app.models.nightline.logger")
def test_delete_instagram_account_succssfull(mock_logger):
    nightline = Nightline.get_nightline("templine")

    assert nightline.delete_instagram_account() is True

    mock_logger.info(f"Instagram account deleted for Nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
def test_delete_instagram_account_no_instagram_acc_added(mock_logger):
    nightline = Nightline.get_nightline("templine")

    assert nightline.delete_instagram_account() is False

    mock_logger.warning(f"No Instagram account configured for nightline '{nightline.name}'.")


# -------------------------
# post_instagram_story
# -------------------------
@patch("app.models.nightline.logger")
def test_post_instagram_story_no_instagram_acc_added(mock_logger):
    nightline = Nightline.get_nightline("templine")

    status_name = "canceled"
    assert nightline.post_instagram_story(status_name) is False

    mock_logger.warning.assert_called_once_with(f"No Instagram account configured for nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
def test_post_instagram_story_bad_status(mock_logger):
    nightline = Nightline.get_nightline("templine")
    nightline.add_instagram_account("test_user", "test_pw")

    status_name = "bad_status_name"
    assert nightline.post_instagram_story(status_name) is False

    mock_logger.warning.assert_called_once_with(f"No status with name '{status_name}' found.")


@patch("app.models.nightline.logger")
@patch("app.models.nightlinestatus.NightlineStatus.get_nightline_status")
def test_post_instagram_story_nightline_status_not_found(mock_get_nightline_status, mock_logger):
    nightline = Nightline.get_nightline("templine")
    Status.add_status("custom_status", "", "", "", "")

    mock_get_nightline_status.return_value = None

    status_name = "custom_status"
    assert nightline.post_instagram_story(status_name) is False

    mock_logger.warning.assert_called_once_with(f"NightlineStatus not found for status '{status_name}' and nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
def test_post_instagram_story_instagram_story_posts_turned_off_for_status(mock_logger):
    nightline = Nightline.get_nightline("templine")

    status_name = "custom_status"
    assert nightline.post_instagram_story(status_name) is False

    mock_logger.info.assert_called_once_with(f"Posting an Instagram story is not configured for status '{status_name}' of nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
def test_post_instagram_story_no_story_slide_configured(mock_logger):
    nightline = Nightline.get_nightline("templine")
    status_name = "custom_status"
    status = Status.get_status(status_name)
    NightlineStatus.update_instagram_story(nightline, status, True)

    assert nightline.post_instagram_story(status_name) is False

    mock_logger.info.assert_called_once_with(f"No Instagram story slide configured for status '{status_name}' of nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.post_story")
@patch("app.models.nightline.NightlineStatus.get_nightline_status")
def test_post_instagram_story_successfull(mock_get_nightline_status, mock_post_story, mock_logger):
    mock_nl_status = MagicMock()
    mock_nl_status.instagram_story = True
    mock_nl_status.instagram_story_slide.path = "/fake/path/to/slide.jpg"
    mock_get_nightline_status.return_value = mock_nl_status

    mock_post_story.return_value = "fake_media_id"

    nightline = Nightline.get_nightline("templine")

    status_name = "custom_status"
    assert nightline.post_instagram_story(status_name) is True

    mock_logger.info.assert_called_once_with(f"Successfully posted Instagram story for status '{status_name}' of nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.post_story")
@patch("app.models.nightline.NightlineStatus.get_nightline_status")
def test_post_instagram_story_posting_fails(mock_get_nightline_status, mock_post_story, mock_logger):
    mock_nl_status = MagicMock()
    mock_nl_status.instagram_story = True
    mock_nl_status.instagram_story_slide.path = "/fake/path/to/slide.jpg"
    mock_get_nightline_status.return_value = mock_nl_status

    mock_post_story.return_value = None

    nightline = Nightline.get_nightline("templine")

    status_name = "custom_status"
    assert nightline.post_instagram_story(status_name) is False

    mock_logger.error.assert_called_once_with(f"Failed to post Instagram story (no media ID returned) for nightline '{nightline.name}'.")


# -------------------------
# delete_instagram_story
# -------------------------
@patch("app.models.nightline.logger")
@patch("app.models.nightline.delete_story_by_id")
def test_delete_instagram_story_delete_story_by_id_fails(mock_delete_story_by_id, mock_logger):
    mock_delete_story_by_id.return_value = False

    nightline = Nightline.get_nightline("templine")

    assert nightline.delete_instagram_story() is False

    mock_logger.error.assert_any_call(f"Failed to delete Instagram story with media ID '{nightline.instagram_media_id}' for nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.delete_story_by_id")
@patch("app.models.nightline.Nightline.set_instagram_media_id")
def test_delete_instagram_story_set_instagram_media_id_fais(mock_set_instagram_media_id, mock_delete_story_by_id, mock_logger):
    mock_delete_story_by_id.return_value = True
    mock_set_instagram_media_id.return_value = False

    nightline = Nightline.get_nightline("templine")

    assert nightline.delete_instagram_story() is False

    mock_logger.error.assert_any_call(f"Story deleted but failed to unset media ID for nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
@patch("app.models.nightline.delete_story_by_id")
def test_delete_instagram_story_successfull(mock_delete_story_by_id, mock_logger):
    mock_delete_story_by_id.return_value = True

    nightline = Nightline.get_nightline("templine")

    assert nightline.delete_instagram_story() is True

    mock_logger.info.assert_any_call(f"Successfully deleted Instagram story for nightline '{nightline.name}'.")


@patch("app.models.nightline.logger")
def test_delete_instagram_story_missing_instagram_media_id(mock_logger):
    nightline = Nightline.get_nightline("templine")

    assert nightline.delete_instagram_story() is True

    mock_logger.debug.assert_any_call("No story to delete because no media id is set")


@patch("app.models.nightline.logger")
def test_delete_instagram_story_no_instagram_acc_added(mock_logger):
    nightline = Nightline.get_nightline("templine")
    nightline.delete_instagram_account()
    nightline.set_instagram_media_id("exampleID")

    assert nightline.delete_instagram_story() is False

    mock_logger.warning.assert_called_once_with(f"No Instagram account configured for nightline '{nightline.name}'.")

    Nightline.remove_nightline("templine")


# -------------------------
# __repr__
# -------------------------
def test_nightline_repr():
    nightline = Nightline()
    nightline.name = "templine"

    assert repr(nightline) == "Nightline('templine')"
