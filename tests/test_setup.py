from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.setup import preinitialize_statuses


@pytest.mark.usefixtures("app_context")
@patch("app.setup.db")
@patch("app.models.status.Status.query")
def test_preinitialize_statuses_adds_missing_statuses(mock_status_query, mock_db):
    mock_status_query.filter_by.return_value.first.return_value = None

    with patch("app.setup.logger") as mock_logger:
        result = preinitialize_statuses()

        assert result is True
        assert mock_db.session.add.call_count == 6
        mock_db.session.commit.assert_called_once()
        mock_logger.info.assert_called_with("Initilized statuses")


@pytest.mark.usefixtures("app_context")
@patch("app.setup.db")
@patch("app.models.status.Status.query")
def test_preinitialize_statuses_skips_existing_statuses(mock_status_query, mock_db):
    mock_status_query.filter_by.return_value.first.return_value = MagicMock()

    with patch("app.setup.logger") as mock_logger:
        result = preinitialize_statuses()

        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_called_once()
        mock_logger.info.assert_called_with("Initilized statuses")
        assert result is True


@pytest.mark.usefixtures("app_context")
@patch("app.setup.logger")
@patch("app.setup.db")
@patch("app.models.status.Status.query")
def test_preinitialize_statuses_rollback_on_exception(mock_status_class, mock_db, mock_logger):
    # Setup: Status.query.filter_by(...).first() → None (Status existiert nicht)
    mock_status_class.query.filter_by.return_value.first.return_value = None

    # Fehler beim Commit simulieren
    mock_db.session.commit.side_effect = SQLAlchemyError("DB error")

    assert preinitialize_statuses() is False

    mock_db.session.rollback.assert_called_once()
    mock_logger.error.assert_called()
