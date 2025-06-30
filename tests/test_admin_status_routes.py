from unittest.mock import patch

import pytest
from flask_restx import abort

from app.config import Config
from app.db import db
from app.models.status import Status

INVALID_API_KEY = "Bearer invalid-token"


@pytest.fixture
def headers_with_valid_token():
    return {"Authorization": Config.ADMIN_API_KEY, "Content-Type": "application/json"}


@pytest.fixture
def headers_with_invalid_token():
    return {"Authorization": INVALID_API_KEY, "Content-Type": "application/json"}


@pytest.fixture
def sample_status_payload():
    return {
        "status_name": "test-status",
        "description_de": "Beschreibung",
        "description_en": "Description",
        "description_now_de": "Jetzt erreichbar",
        "description_now_en": "Available now",
    }


# -------------------------
# admin/status/ [post]
# -------------------------
def test_add_status_success(client, headers_with_valid_token, sample_status_payload):
    response = client.post("/admin/status/", json=sample_status_payload, headers=headers_with_valid_token)
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "test-status" in data["message"]

    # Cleanup
    status = Status.query.filter_by(name="test-status").first()
    if status:
        db.session.delete(status)
        db.session.commit()


def test_add_status_missing_token(client, sample_status_payload):
    response = client.post("/admin/status/", json=sample_status_payload)
    assert response.status_code == 401
    assert "message" in response.get_json()


def test_add_status_invalid_token(client, headers_with_invalid_token, sample_status_payload):
    response = client.post("/admin/status/", json=sample_status_payload, headers=headers_with_invalid_token)
    assert response.status_code == 403
    assert "message" in response.get_json()


def test_add_status_missing_fields(client, headers_with_valid_token):
    payload = {
        "status_name": "incomplete-status",
        "description_de": "Fehlt was",
        # missing required fields
    }

    response = client.post("/admin/status/", json=payload, headers=headers_with_valid_token)
    assert response.status_code == 400
    data = response.get_json()
    assert "message" in data


def test_add_duplicate_status(client, headers_with_valid_token, sample_status_payload):
    # Add status once
    client.post("/admin/status/", json=sample_status_payload, headers=headers_with_valid_token)

    # Try to add it again
    response = client.post("/admin/status/", json=sample_status_payload, headers=headers_with_valid_token)
    assert response.status_code == 400
    data = response.get_json()
    assert f"Status '{sample_status_payload['status_name']}' could not be added" in data.get("message", "")

    # Cleanup
    status = Status.query.filter_by(name="test-status").first()
    if status:
        db.session.delete(status)
        db.session.commit()


# -------------------------
# admin/status/ [delete]
# -------------------------
def test_delete_status_success(client, headers_with_valid_token):

    Status.add_status("delete-me", "", "", "", "")

    response = client.delete(
        "/admin/status/",
        json={"status": "delete-me"},
        headers=headers_with_valid_token,
    )

    assert response.status_code == 200
    assert response.json == {"message": "Status 'delete-me' removed successfully"}
    assert Status.get_status("delete-me") is None


def test_delete_status_not_found(client, headers_with_valid_token):
    response = client.delete(
        "/admin/status/",
        json={"status": "non-existent"},
        headers=headers_with_valid_token,
    )

    assert response.status_code == 400
    assert "could not be removed" in response.json["message"]


def test_delete_status_missing_field(client, headers_with_valid_token):
    response = client.delete(
        "/admin/status/",
        json={},
        headers=headers_with_valid_token,
    )

    assert response.status_code == 400
    assert "Missing 'status' in request" in response.json["message"]


def test_delete_status_invalid_value(client, headers_with_valid_token):
    response = client.delete(
        "/admin/status/",
        json={"status": "invalid value"},
        headers=headers_with_valid_token,
    )

    assert response.status_code == 400
    assert "Status 'invalid value' could not be removed" in response.json["message"]


def test_delete_status_unauthorized(client):
    # Act
    response = client.delete(
        "/admin/status/",
        json={"status": "something"},
        headers={},
    )

    assert response.status_code == 401


# -------------------------
# admin/status/all [get]
# -------------------------
def test_list_statuses_success(client, headers_with_valid_token):
    response = client.get(
        "/admin/status/all",
        headers=headers_with_valid_token,
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 6

    assert response.json[0]["status_name"] == "default"
    assert response.json[0]["description_de"] == ""
    assert response.json[0]["description_en"] == ""
    assert response.json[0]["description_now_de"] == "Wir sind jetzt erreichbar 📞"
    assert response.json[0]["description_now_en"] == "We're now available 📞"


@patch("app.routes.admin.admin_status_routes.Status.list_statuses")
def test_list_statuses_not_found(mock_list_statuses, client, headers_with_valid_token):
    mock_list_statuses.return_value = []

    response = client.get(
        "/admin/status/all",
        headers=headers_with_valid_token,
    )

    assert response.status_code == 404
    assert response.json["message"] == "No statuses found"
