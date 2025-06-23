from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError


from app.models.nightline import Nightline
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
    status = Status.get_status("english")
    assert nightline.set_status("english") == status

    mock_logger.debug.assert_any_call(f"Set status of nightline '{nightline.name}' to: 'english'")
    mock_logger.info.assert_called_once_with(f"Status 'english' set successfully")

@patch("app.models.nightline.logger")
def test_set_status_no_valid_status(mock_logger):
    nightline = Nightline.get_nightline("templine")
    assert nightline.set_status("bsod") == None

    mock_logger.debug.assert_any_call(f"Set status of nightline '{nightline.name}' to: 'bsod'")

@patch("app.models.nightline.logger")
@patch("app.models.status.Status.get_status")
def test_set_status_exception(mock_get_status, mock_logger):
    mock_get_status.side_effect = Exception("Unknown Error")

    nightline = Nightline.get_nightline("templine")
    assert nightline.set_status("bsod") == None

    mock_logger.debug.assert_any_call(f"Set status of nightline '{nightline.name}' to: 'bsod'")
    mock_logger.error.assert_called_once_with(f"Failed to set status 'bsod' for nightline '{nightline.name}': Unknown Error")


# -------------------------
# reset_status
# -------------------------
@patch("app.models.nightline.logger")
def test_reset_status_successfull(mock_logger):
    nightline = Nightline.get_nightline("templine")
    status = Status.get_status("default")
    
    assert nightline.reset_status() == status

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
