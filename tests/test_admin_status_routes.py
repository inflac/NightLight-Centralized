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


def assert_message(response, expected_substring, status_code):
    assert response.status_code == status_code
    data = response.get_json()
    assert "message" in data
    assert expected_substring in data["message"]


# -------------------------
# admin/status/ [post]
# -------------------------
def test_add_status_success(client, headers_with_valid_token, sample_status_payload):
    response = client.post("/admin/status/", json=sample_status_payload, headers=headers_with_valid_token)
    assert_message(response, "test-status", 200)

    # Cleanup
    status = Status.query.filter_by(name="test-status").first()
    if status:
        db.session.delete(status)
        db.session.commit()


def test_add_status_missing_token(client, sample_status_payload):
    response = client.post("/admin/status/", json=sample_status_payload)
    assert_message(response, "Missing Authorization header", 401)


def test_add_status_invalid_token(client, headers_with_invalid_token, sample_status_payload):
    response = client.post("/admin/status/", json=sample_status_payload, headers=headers_with_invalid_token)
    assert_message(response, "Admin API key required", 403)


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
    assert_message(response, f"Status '{sample_status_payload['status_name']}' could not be added", 400)

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
    assert_message(response, "Status 'delete-me' removed successfully", 200)

    assert Status.get_status("delete-me") is None


def test_delete_status_not_found(client, headers_with_valid_token):
    response = client.delete(
        "/admin/status/",
        json={"status": "non-existent"},
        headers=headers_with_valid_token,
    )
    assert_message(response, "could not be removed", 400)


def test_delete_status_missing_field(client, headers_with_valid_token):
    response = client.delete(
        "/admin/status/",
        json={},
        headers=headers_with_valid_token,
    )
    assert_message(response, "Missing 'status' in request", 400)


def test_delete_status_invalid_value(client, headers_with_valid_token):
    response = client.delete(
        "/admin/status/",
        json={"status": "invalid value"},
        headers=headers_with_valid_token,
    )
    assert_message(response, "Status 'invalid value' could not be removed", 400)


def test_delete_status_unauthorized(client):
    response = client.delete(
        "/admin/status/",
        json={"status": "something"},
        headers={},
    )
    assert_message(response, "Missing Authorization header", 401)


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
    assert_message(response, "No statuses found", 404)
