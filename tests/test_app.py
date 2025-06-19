import os
from unittest.mock import patch

import pytest
from sqlalchemy.exc import OperationalError

from app.app import create_app

config_overrides = {
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "ENABLE_ADMIN_ROUTES": False,
    "API_DOC_PATH": False,
}


# -------------------------
# create_app
# -------------------------


def test_create_app_suppresses_known_operational_error():
    with patch("app.app.db.create_all") as mock_create_all:
        mock_create_all.side_effect = OperationalError("table statuses already exists", None, None)
        app = create_app(config_overrides)
        assert app is not None


def test_create_app_raises_unknown_operational_error():
    with patch("app.app.db.create_all") as mock_create_all:
        mock_create_all.side_effect = OperationalError("some other DB error", None, None)
        with pytest.raises(OperationalError):
            create_app()


@patch("app.config.Config.ENABLE_ADMIN_ROUTES", True)
def test_admin_routes_enabled():
    app = create_app(config_overrides)
    client = app.test_client()
    assert client.get("/admin/status/all").status_code == 200


@patch("app.config.Config.ENABLE_ADMIN_ROUTES", False)
def test_admin_routes_disabled():
    app = create_app(config_overrides)
    client = app.test_client()
    assert client.get("/admin/status/all").status_code == 404
