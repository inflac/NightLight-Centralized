import pytest

from app.app import create_app


@pytest.fixture(scope="session")
def app():
    overrides = {
        "TESTING": True,
        "ENCRYPTION_PASSWORD": "testpassword",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "ENABLE_ADMIN_ROUTES": False,
        "API_DOC_PATH": False,
    }
    app = create_app(overrides)

    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
