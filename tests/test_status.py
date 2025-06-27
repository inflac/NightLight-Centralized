
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

from app.models.status import Status
from app.models.nightlinestatus import NightlineStatus

# -------------------------
# get_status
# -------------------------
@patch("app.models.status.logger")
def test_get_status_successfull(mock_logger):
    status_name = "default"

    assert isinstance(Status.get_status(status_name), Status)

    mock_logger.debug.assert_any_call(f"Fetching status by name: {status_name}")
    mock_logger.debug.assert_any_call(f"Found status: {status_name}")

@patch("app.models.status.logger")
def test_get_status_not_found(mock_logger):
    status_name = "unknown_status"

    assert Status.get_status(status_name) is None

    mock_logger.debug.assert_any_call(f"Fetching status by name: {status_name}")
    mock_logger.info.assert_any_call(f"Status '{status_name}' not found")


# -------------------------
# add_status
# -------------------------
@patch("app.models.status.logger")
def test_add_status_already_exists(mock_logger):
    status_name = "default"

    assert Status.add_status(status_name, "", "", "", "") is None

    mock_logger.debug.assert_any_call(f"Adding new status: {status_name}")
    mock_logger.warning.assert_any_call(f"Status '{status_name}' already exists")

@patch("app.models.status.logger")
def test_add_status_successfully(mock_logger):
    status_name = "new_status"

    assert isinstance(Status.add_status(status_name, "", "", "", ""), Status)

    mock_logger.debug.assert_called_once_with(f"Adding new status: {status_name}")
    mock_logger.info.assert_called_once_with(f"Status '{status_name}' added successfully")

@patch("app.models.status.logger")
@patch("app.models.status.db.session.commit")
def test_add_status_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")
    status_name = "new_status_123"

    assert Status.add_status(status_name, "", "", "", "") is None

    mock_logger.debug.assert_called_once_with(f"Adding new status: {status_name}")
    mock_logger.error.assert_called_once_with(f"Error adding status '{status_name}': Database error")


# -------------------------
# remove_status
# -------------------------
@patch("app.models.status.logger")
def test_remove_status_do_not_exist(mock_logger):
    status_name = "not_existing_status"

    assert Status.remove_status(status_name) is None

    mock_logger.debug.assert_any_call(f"Removing status: {status_name}")
    mock_logger.warning.assert_called_once_with(f"Status '{status_name}' not found, nothing to remove")

@patch("app.models.status.logger")
@patch("app.models.status.db.session.commit")
def test_remove_status_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    status_name = "default"
    amount_nl_statuses = len(NightlineStatus.query.all())

    assert Status.remove_status(status_name) is None
    
    assert amount_nl_statuses == len(NightlineStatus.query.all())

    mock_logger.debug.assert_any_call(f"Removing status: {status_name}")
    mock_logger.error.assert_called_once_with(f"Error removing status '{status_name}': Database error")

@patch("app.models.status.logger")
def test_remove_status_(mock_logger):
    status_name = "new_status"
    
    assert isinstance(Status.remove_status(status_name), Status)

    mock_logger.debug.assert_any_call(f"Removing status: {status_name}")
    mock_logger.info.assert_called_once_with(f"Status '{status_name}' removed successfully")


# -------------------------
# list_statuses
# -------------------------
@patch("app.models.status.logger")
def test_list_statuses(mock_logger):
    amount_statuses = len(Status.query.all())

    result = Status.list_statuses()
    assert len(result) > 6
    assert isinstance(result[0], Status)

    mock_logger.debug.assert_called_once_with("Listing all statuses")
    mock_logger.info.assert_called_once_with(f"Listed {amount_statuses} statuses")

@patch("app.models.status.logger")
@patch("app.models.status.Status.query")
def test_list_statuses(mock_query, mock_logger):
    mock_query.all.side_effect = SQLAlchemyError("Database error")

    assert Status.list_statuses() == []

    mock_logger.debug.assert_called_once_with("Listing all statuses")
    mock_logger.error.assert_called_once_with(f"Error while fetching the statuses: Database error")


# -------------------------
# __repr__
# -------------------------
def test_status_repr():
    status = Status(name="test")

    assert repr(status) == "Status('test')"
