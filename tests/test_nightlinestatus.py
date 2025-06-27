from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models.nightline import Nightline
from app.models.nightlinestatus import NightlineStatus
from app.models.status import Status


# -------------------------
# get_nightline_status
# -------------------------
def test_get_nightline_status_successfull():
    nightline = Nightline.add_nightline("nightlinestatus_line_1")
    assert isinstance(NightlineStatus.get_nightline_status(nightline.id, nightline.status.id), NightlineStatus)


def test_get_nightline_status_wrong_nightline_id():
    nightline = Nightline.get_nightline("nightlinestatus_line_1")
    assert NightlineStatus.get_nightline_status(100, nightline.status.id) is None


def test_get_nightline_status_wrong_status_id():
    nightline = Nightline.get_nightline("nightlinestatus_line_1")
    assert NightlineStatus.get_nightline_status(nightline.id, 100) is None
    Nightline.remove_nightline("nightlinestatus_line_1")


# -------------------------
# add_new_status_for_all_nightlines
# -------------------------
@patch("app.models.nightlinestatus.logger")
def test_add_new_status_for_all_nightlines_successfull(mock_logger):
    new_status = Status(id=10, name="new_status", description_de="", description_en="", description_now_de="", description_now_en="")
    db.session.add(new_status)
    db.session.commit()

    assert NightlineStatus.add_new_status_for_all_nightlines(new_status) is True

    mock_logger.debug.assert_called_once_with(f"Creating NightlineStatus entries for all nightlines with status '{new_status.name}'")
    mock_logger.info.assert_called_once_with(f"NightlineStatus entries created successfully for status '{new_status.name}'")


@patch("app.models.nightlinestatus.logger")
@patch("app.models.nightlinestatus.db.session.commit")
def test_add_new_status_for_all_nightlines_database_error_missing_status_id(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    status = Status.get_status("new_status")

    assert NightlineStatus.add_new_status_for_all_nightlines(status) is False

    mock_logger.debug.assert_called_once_with(f"Creating NightlineStatus entries for all nightlines with status '{status.name}'")
    mock_logger.error.assert_called_once_with(f"Error creating NightlineStatus entries for status '{status.name}': Database error")


# -------------------------
# add_statuses_for_new_nightlines
# -------------------------
@patch("app.models.nightlinestatus.logger")
@patch("app.models.nightlinestatus.db.session.add")
def test_add_statuses_for_new_nightlines_database_error(mock_add, mock_logger):
    mock_add.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline(name="nightlinestatus_line_2", status_id=Status.get_status("default").id, now=False, instagram_media_id="")

    assert NightlineStatus.add_statuses_for_new_nightlines(nightline) is False

    mock_logger.debug.assert_called_once_with(f"Creating NightlineStatus entries for all statuses for nightline '{nightline.name}'")
    mock_logger.error.assert_called_once_with(f"Error creating NightlineStatus entries for nightline '{nightline.name}': Database error")


@patch("app.models.nightlinestatus.logger")
def test_add_statuses_for_new_nightlines_successfull(mock_logger):
    nightline = Nightline(name="nightlinestatus_line_2", status_id=Status.get_status("default").id, now=False, instagram_media_id="")
    db.session.add(nightline)
    db.session.commit()

    assert NightlineStatus.add_statuses_for_new_nightlines(nightline) is True

    all_nls = NightlineStatus.query.filter_by(nightline_id=nightline.id).all()
    assert len(all_nls) == len(Status.query.all())

    for nls in all_nls:
        assert nls.instagram_story is False

    mock_logger.debug.assert_called_once_with(f"Creating NightlineStatus entries for all statuses for nightline '{nightline.name}'")
    mock_logger.info.assert_called_once_with(f"NightlineStatus entries created successfully for nightline '{nightline.name}'")

    Nightline.remove_nightline("nightlinestatus_line_2")


# -------------------------
# delete_status_for_all_nightlines
# -------------------------
@patch("app.models.nightlinestatus.logger")
@patch("app.models.nightlinestatus.db.session.commit")
def test_delete_status_for_all_nightlines_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    status = Status.get_status("default")

    assert NightlineStatus.delete_status_for_all_nightlines(status) is False

    mock_logger.debug.assert_called_once_with(f"Deleting NightlineStatus entries for status: '{status.name}'")
    mock_logger.error.assert_called_once_with(f"Error deleting NightlineStatus entries for status: '{status.name}': Database error")


@patch("app.models.nightlinestatus.logger")
def test_delete_status_for_all_nightlines_no_nightlinestatuses_deleted(mock_logger):
    new_status = Status(id=11, name="no_nightline_statuses_status", description_de="", description_en="", description_now_de="", description_now_en="")

    assert NightlineStatus.delete_status_for_all_nightlines(new_status) is False

    mock_logger.debug.assert_called_once_with(f"Deleting NightlineStatus entries for status: '{new_status.name}'")
    mock_logger.warning.assert_called_once_with(f"No NightlineStatus entries found for status: '{new_status.name}'")


@patch("app.models.nightlinestatus.logger")
def test_delete_status_for_all_nightlines_successfull(mock_logger):
    status = Status.get_status("new_status")
    amount_nls = len(Nightline.list_nightlines())

    assert NightlineStatus.delete_status_for_all_nightlines(status) is True

    mock_logger.debug.assert_called_once_with(f"Deleting NightlineStatus entries for status: '{status.name}'")
    mock_logger.info.assert_called_once_with(f"Successfully deleted '{amount_nls}' NightlineStatus entries for status: '{status.name}'")

    db.session.delete(status)
    db.session.commit()


# -------------------------
# delete_statuses_for_nightline
# -------------------------
@patch("app.models.nightlinestatus.logger")
def test_delete_statuses_for_nightline_no_nightlinestatuses_deleted(mock_logger):
    nightline = Nightline(name="no_nightline_statuses_nightline", status_id=Status.get_status("default").id, now=False, instagram_media_id="")

    assert NightlineStatus.delete_statuses_for_nightline(nightline) is False

    mock_logger.debug(f"Deleting all NightlineStatus entries for nightline: '{nightline.name}'")
    mock_logger.warning(f"No NightlineStatus entries found for nightline: '{nightline.name}'")


@patch("app.models.nightlinestatus.logger")
def test_delete_statuses_for_nightline_successfull(mock_logger):
    nightline = Nightline.add_nightline("nightlinestatus_line_3")
    amount_statuses = len(Status.list_statuses())

    assert NightlineStatus.delete_statuses_for_nightline(nightline) is True

    mock_logger.debug(f"Deleting all NightlineStatus entries for nightline: '{nightline.name}'")
    mock_logger.info(f"Successfully deleted '{amount_statuses}' NightlineStatus entries for nightline: '{nightline.name}'")

    NightlineStatus.add_statuses_for_new_nightlines(nightline)


@patch("app.models.nightlinestatus.logger")
@patch("app.models.nightlinestatus.db.session.commit")
def test_delete_statuses_for_nightline_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("nightlinestatus_line_3")

    assert NightlineStatus.delete_statuses_for_nightline(nightline) is False

    mock_logger.debug(f"Deleting all NightlineStatus entries for nightline: '{nightline.name}'")
    mock_logger.error(f"Error deleting NightlineStatus entries for nightline: '{nightline.name}': Database error")

    Nightline.remove_nightline(nightline.name)


# -------------------------
# update_instagram_story
# -------------------------
@patch("app.models.nightlinestatus.logger")
def test_update_instagram_story_successfull(mock_logger):
    nightline = Nightline.add_nightline("nightlinestatus_line_4")
    status = Status.get_status("english")

    assert NightlineStatus.update_instagram_story(nightline, status, True) is True

    mock_logger.debug.assert_any_call(f"Updating instagram_story for nightline: '{nightline.name}' and status: '{status.name}' to 'True'")
    mock_logger.info.assert_any_call(f"Updated instagram_story for nightline: '{nightline.name}', status: '{status.name}' to 'True'")


@patch("app.models.nightlinestatus.logger")
@patch("app.models.nightlinestatus.db.session.commit")
def test_update_instagram_story_database_error(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("Database error")

    nightline = Nightline.get_nightline("nightlinestatus_line_4")
    status = Status.get_status("english")

    assert NightlineStatus.update_instagram_story(nightline, status, True) is False

    mock_logger.debug.assert_called_once_with(f"Updating instagram_story for nightline: '{nightline.name}' and status: '{status.name}' to 'True'")
    mock_logger.error.assert_called_once_with(f"Error updating instagram_story for nightline: '{nightline.name}', status: '{status.name}': Database error")


@patch("app.models.nightlinestatus.logger")
def test_update_instagram_story_no_nightlinestatuses_found(mock_logger):
    nightline = Nightline.get_nightline("nightlinestatus_line_4")
    status = Status(id=11, name="no_nightline_statuses_status", description_de="", description_en="", description_now_de="", description_now_en="")

    assert NightlineStatus.update_instagram_story(nightline, status, False) is False

    mock_logger.debug.assert_called_once_with(f"Updating instagram_story for nightline: '{nightline.name}' and status: '{status.name}' to 'False'")
    mock_logger.warning.assert_called_once_with(f"No NightlineStatus entry found for nightline: '{nightline.name}' and status: {status.name}")

    Nightline.remove_nightline(nightline.name)
