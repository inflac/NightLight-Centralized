from unittest.mock import patch

import pytest

from app.config import Config
from app.models.nightline import Nightline


@pytest.fixture
def headers_with_valid_token():
    return {"Authorization": Config.ADMIN_API_KEY, "Content-Type": "application/json"}


@pytest.fixture
def add_test_nightline():
    nightline = Nightline.add_nightline("testline")
    yield nightline
    Nightline.remove_nightline("testline")


def assert_message(response, expected_substring, status_code):
    assert response.status_code == status_code
    data = response.get_json()
    assert "message" in data
    assert expected_substring in data["message"]


# -------------------------
# admin/nightline/<nightline_name> [get]
# -------------------------
def test_get_nightline_not_found(client, headers_with_valid_token):
    response = client.get("/admin/nightline/nonexisting", headers=headers_with_valid_token)

    assert_message(response, "Nightline 'nonexisting' not found", 404)


def test_get_nightline_success(client, headers_with_valid_token, add_test_nightline):
    response = client.get(f"/admin/nightline/{add_test_nightline.name}", headers=headers_with_valid_token)
    assert response.status_code == 200

    data = response.get_json()

    assert data["nightline_id"] == add_test_nightline.id
    assert data["nightline_name"] == add_test_nightline.name
    assert data["status_name"] == add_test_nightline.status.name
    assert data["instagram_media_id"] == add_test_nightline.instagram_media_id
    assert data["now"] == add_test_nightline.now


# -------------------------
# admin/nightline/<nightline_name> [post]
# -------------------------
def test_add_nightline_success(client, headers_with_valid_token):
    response = client.post("/admin/nightline/testline", headers=headers_with_valid_token)

    assert_message(response, "Nightline 'testline' added successfully", 200)


def test_add_nightline_existing(client, headers_with_valid_token):
    response = client.post("/admin/nightline/testline", headers=headers_with_valid_token)

    assert_message(response, "Nightline 'testline' already exists", 400)

    Nightline.remove_nightline("testline")


@patch("app.routes.admin.admin_nightline_routes.Nightline.add_nightline", return_value=False)
def test_add_nightline_error_on_add_nightline(mock_add_nightline, client, headers_with_valid_token):

    response = client.post("/admin/nightline/testline", headers=headers_with_valid_token)

    assert_message(response, "Nightline 'testline' could not be added due to invalid data or duplication", 400)

    Nightline.remove_nightline("testline")


# -------------------------
# admin/nightline/<nightline_name> [delete]
# -------------------------
def test_delete_nightline_non_existing(client, headers_with_valid_token):
    response = client.delete("/admin/nightline/testline", headers=headers_with_valid_token)

    assert_message(response, "Nightline 'testline' could not be removed", 400)


def test_delete_nightline_success(client, headers_with_valid_token):
    nightline = Nightline.add_nightline("testline")

    response = client.delete(f"/admin/nightline/{nightline.name}", headers=headers_with_valid_token)

    assert_message(response, f"Nightline '{nightline.name}' removed successfully", 200)


# -------------------------
# admin/nightline/key/<nightline_name> [get]
# -------------------------
def test_get_nightline_api_key_non_existing_nightline(client, headers_with_valid_token):
    response = client.get("/admin/nightline/key/testline", headers=headers_with_valid_token)

    assert_message(response, "Nightline 'testline' not found", 404)


def test_get_nightline_api_key_success(client, headers_with_valid_token):
    nightline = Nightline.add_nightline("testline")

    response = client.get(f"/admin/nightline/key/{nightline.name}", headers=headers_with_valid_token)
    assert response.status_code == 200

    data = response.get_json()
    assert "API-Key" in data


@patch("app.routes.admin.admin_nightline_routes.Nightline.get_api_key", return_value=None)
def test_get_nightline_api_key_not_found(mock_get_api_key, client, headers_with_valid_token):

    response = client.get(f"/admin/nightline/key/testline", headers=headers_with_valid_token)
    assert_message(response, "No api key found for nightline: 'testline'", 500)


# -------------------------
# admin/nightline/key/<nightline_name> [patch]
# -------------------------
def test_renew_nightline_api_key_success(client, headers_with_valid_token):
    response = client.patch("/admin/nightline/key/testline", headers=headers_with_valid_token)

    assert_message(response, "API key regenerated successfully", 200)


@patch("app.routes.admin.admin_nightline_routes.Nightline.renew_api_key", return_value=None)
def test_renew_nightline_api_key_not_found_api_key(mock_renew_api_key, client, headers_with_valid_token):
    response = client.patch("/admin/nightline/key/testline", headers=headers_with_valid_token)

    assert_message(response, "No api key found for nightline: 'testline'", 500)

    Nightline.remove_nightline("testline")


def test_renew_nightline_api_key_nightline_not_found(client, headers_with_valid_token):
    response = client.patch("/admin/nightline/key/testline", headers=headers_with_valid_token)

    assert_message(response, "Nightline 'testline' not found", 404)
