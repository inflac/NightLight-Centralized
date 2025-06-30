from unittest.mock import patch

import pytest
from app.models.nightline import Nightline
from app.models.nightlinestatus import NightlineStatus
from app.config import Config



@pytest.fixture
def auth_header_needs_key():
    return {
        "Authorization": "",
        "Content-Type": "application/json"
    }


# -------------------------
# require_api_key [decorator]
# -------------------------
def test_set_status_missing_auth_header(client):
    response = client.patch("/nightline/testline/status",)

    assert response.status_code == 401
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Missing Authorization header"

def test_set_status_using_admin_api_key_nightline_not_found(client, auth_header_needs_key):
    payload = {"status": "english"}

    auth_header_needs_key["Authorization"] = Config.ADMIN_API_KEY

    response = client.patch(
        "/nightline/testline/status",
        headers=auth_header_needs_key,
        json=payload,
    )

    assert response.status_code == 404

def test_require_api_key_nightline_in_kwargs_invalid_key(client):
    headers = {"Authorization": "invalid-key"}

    response = client.patch("/nightline/testline/status", headers=headers, json={"status": "english"})

    assert response.status_code == 403
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Invalid API key"


# -------------------------
# nightline/<nightline_name>/status [patch]
# -------------------------
def test_set_status_success(client, auth_header_needs_key):
    nightline = Nightline.add_nightline("testline")

    payload = {"status": "english"}

    auth_header_needs_key["Authorization"] = nightline.get_api_key().key

    response = client.patch(
        "/nightline/testline/status",
        headers=auth_header_needs_key,
        json=payload,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Status successfully updated to: 'english'"

def test_set_status_invalid_status(client, auth_header_needs_key):
    nightline = Nightline.get_nightline("testline")

    payload = {"status": "invalid"}

    auth_header_needs_key["Authorization"] = nightline.get_api_key().key

    response = client.patch(
        "/nightline/testline/status",
        headers=auth_header_needs_key,
        json=payload,
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Updating the status failed"

@patch("app.routes.nightline.nightline_routes.Nightline.post_instagram_story")
def test_set_status_posting_story_slide_fails(mock_post_instagram_story, client, auth_header_needs_key):
    mock_post_instagram_story.return_value = False

    nightline = Nightline.get_nightline("testline")
    NightlineStatus.update_instagram_story(nightline, nightline.status, True)

    payload = {"status": "english"}

    auth_header_needs_key["Authorization"] = nightline.get_api_key().key

    response = client.patch(
        "/nightline/testline/status",
        headers=auth_header_needs_key,
        json=payload,
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Status updated but uploading an instagram story post failed"

@patch("app.routes.nightline.nightline_routes.Nightline.post_instagram_story")
def test_set_status_posting_story_slide_success(mock_post_instagram_story, client, auth_header_needs_key):
    mock_post_instagram_story.return_value = True

    nightline = Nightline.get_nightline("testline")
    NightlineStatus.update_instagram_story(nightline, nightline.status, True)

    payload = {"status": "english"}

    auth_header_needs_key["Authorization"] = nightline.get_api_key().key

    response = client.patch(
        "/nightline/testline/status",
        headers=auth_header_needs_key,
        json=payload,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Status successfully updated to: 'english'"


# -------------------------
# nightline/<nightline_name>/status [delete]
# -------------------------
def test_reset_status_nightline_not_found(client, auth_header_needs_key):
    auth_header_needs_key["Authorization"] = Config.ADMIN_API_KEY

    response = client.delete(
        "/nightline/invalidnightline/status",
        headers=auth_header_needs_key,
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Nightline 'invalidnightline' not found"

@patch("app.routes.nightline.nightline_routes.Nightline.reset_status")
def test_reset_status_resetting_failes(mock_reset_status, client, auth_header_needs_key):
    mock_reset_status.return_value = False

    nightline = Nightline.get_nightline("testline")
    
    auth_header_needs_key["Authorization"] = Config.ADMIN_API_KEY

    response = client.delete(
        f"/nightline/{nightline.name}/status",
        headers=auth_header_needs_key,
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Resetting the status failed"

@patch("app.routes.nightline.nightline_routes.Nightline.delete_instagram_story")
def test_reset_status_deleting_instagram_story_fails(mock_delete_instagram_story, client, auth_header_needs_key):
    mock_delete_instagram_story.return_value = False

    nightline = Nightline.get_nightline("testline")
    nightline.set_instagram_media_id("exampleID")
    
    auth_header_needs_key["Authorization"] = Config.ADMIN_API_KEY

    response = client.delete(
        f"/nightline/{nightline.name}/status",
        headers=auth_header_needs_key,
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Staus successfully reset but deleting the current instagram story failed"

@patch("app.routes.nightline.nightline_routes.Nightline.delete_instagram_story")
def test_reset_status_success(mock_delete_instagram_story, client, auth_header_needs_key):
    mock_delete_instagram_story.return_value = True
    
    nightline = Nightline.get_nightline("testline")
    
    auth_header_needs_key["Authorization"] = Config.ADMIN_API_KEY

    response = client.delete(
        f"/nightline/{nightline.name}/status",
        headers=auth_header_needs_key,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Status successfully reset to: 'default'"

    Nightline.remove_nightline("testline")