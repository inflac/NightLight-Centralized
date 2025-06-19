import importlib
import sys
from unittest.mock import patch

import pytest
from flask import Flask


# -------------------------
# Config
# -------------------------
def test_config_encryption_password_not_set():
    sys.modules.pop("app.config", None)  # Ensure fresh import

    with patch("os.getenv", side_effect=lambda key, default=None: None if key == "ENCRYPTION_PASSWORD" else default):
        with pytest.raises(ValueError, match="ENCRYPTION_PASSWORD is not set in .env!"):
            import app.config


# -------------------------
# Config.configure_cors
# -------------------------
@pytest.mark.parametrize(
    "allowed_websites_env, request_origin, expected_allow_origin",
    [
        ("*", "https://example.com", "https://example.com"),
        ("specific.com", "https://specific.com", None),  # missing scheme
        ("https://specific.com", "https://specific.com", "https://specific.com"),
        ("https://test1.com, https://test2.com", "https://test1.com", "https://test1.com"),
        (None, "https://not-allowed.com", None),
        ("", "https://not-allowed.com", None),
    ],
)
def test_cors_behavior(allowed_websites_env, request_origin, expected_allow_origin):
    # Ensure config is re-imported freshly
    sys.modules.pop("app.config", None)

    def getenv_side_effect(key, default=None):
        if key == "CORS_ALLOWED_WEBSITES":
            return allowed_websites_env
        if key == "ENCRYPTION_PASSWORD":
            return "dummy"
        return default

    with patch("os.getenv", side_effect=getenv_side_effect):
        import app.config

        importlib.reload(app.config)

        flask_app = Flask(__name__)
        flask_app.config.from_object(app.config.Config)
        app.config.Config.configure_cors(flask_app)

        @flask_app.route("/test")
        def test():
            return "ok"

        with flask_app.test_client() as client:
            resp = client.get("/test", headers={"Origin": request_origin})
            assert resp.status_code == 200
            cors_header = resp.headers.get("Access-Control-Allow-Origin", None)
            assert cors_header == expected_allow_origin
