from unittest.mock import patch

import pytest
from app.models.nightline import Nightline
from app.config import Config



@pytest.fixture
def headers_with_valid_token():
    return {
        "Authorization": Config.ADMIN_API_KEY,
        "Content-Type": "application/json"
    }


# -------------------------
# admin/nightline/<nightline_name> [get]
# -------------------------
def test_get_nightline_not_found(client, headers_with_valid_token):
    response = client.get("/admin/nightline/nonexisting", headers=headers_with_valid_token)

    assert response.status_code == 404

    data = response.get_json()
    
    assert "message" in data
    assert "Nightline 'nonexisting' not found" in data["message"]

def test_get_nightline_success(client, headers_with_valid_token):
    nightline = Nightline.add_nightline("testline")

    # Act
    response = client.get(f"/admin/nightline/{nightline.name}", headers=headers_with_valid_token)
    assert response.status_code == 200

    data = response.get_json()

    # Assert
    assert data["nightline_id"] == nightline.id
    assert data["nightline_name"] == nightline.name
    assert data["status_name"] == nightline.status.name
    assert data["instagram_media_id"] == nightline.instagram_media_id
    assert data["now"] == nightline.now

    Nightline.remove_nightline(nightline.name)


# -------------------------
# admin/nightline/<nightline_name> [post]
# -------------------------
def test_add_nightline_success(client, headers_with_valid_token):
    response = client.post("/admin/nightline/testline", headers=headers_with_valid_token)

    assert response.status_code == 200

    data = response.get_json()
    
    assert "message" in data
    assert "Nightline 'testline' added successfully" in data["message"]

def test_add_nightline_existing(client, headers_with_valid_token):
    response = client.post("/admin/nightline/testline", headers=headers_with_valid_token)

    assert response.status_code == 400

    data = response.get_json()

    assert "message" in data
    assert "Nightline 'testline' could not be added due to invalid data or duplication" in data["message"]

    Nightline.remove_nightline("testline")


# -------------------------
# admin/nightline/<nightline_name> [delete]
# -------------------------
def test_delete_nightline_non_existing(client, headers_with_valid_token):
    response = client.delete("/admin/nightline/testline", headers=headers_with_valid_token)

    assert response.status_code == 400

    data = response.get_json()

    assert "message" in data
    assert "Nightline 'testline' could not be removed" in data["message"]


def test_delete_nightline_success(client, headers_with_valid_token):
    nightline = Nightline.add_nightline("testline")
    
    response = client.delete(f"/admin/nightline/{nightline.name}", headers=headers_with_valid_token)

    assert response.status_code == 200

    data = response.get_json()
    
    assert "message" in data
    assert f"Nightline '{nightline.name}' removed successfully" in data["message"]


# -------------------------
# admin/nightline/key/<nightline_name> [get]
# -------------------------
def test_get_nightline_api_key_non_existing_nightline(client, headers_with_valid_token):
    response = client.get("/admin/nightline/key/testline", headers=headers_with_valid_token)

    assert response.status_code == 404

    data = response.get_json()

    assert "message" in data
    assert "Nightline 'testline' not found" in data["message"]

def test_get_nightline_api_key_success(client, headers_with_valid_token):
    nightline = Nightline.add_nightline("testline")
    
    response = client.get(f"/admin/nightline/key/{nightline.name}", headers=headers_with_valid_token)
    assert response.status_code == 200
    
    data = response.get_json()
    assert "API-Key" in data

@patch("app.routes.admin.admin_nightline_routes.Nightline.get_api_key")
def test_get_nightline_api_key_not_found(mock_get_api_key, client, headers_with_valid_token):
    mock_get_api_key.return_value = None
    
    response = client.get(f"/admin/nightline/key/testline", headers=headers_with_valid_token)
    assert response.status_code == 500

    data = response.get_json()
    assert "message" in data
    assert "No api key found for nightline: 'testline'" in data["message"]


# -------------------------
# admin/nightline/key/<nightline_name> [patch]
# -------------------------
def test_renew_nightline_api_key_success(client, headers_with_valid_token):
    response = client.patch("/admin/nightline/key/testline", headers=headers_with_valid_token)

    assert response.status_code == 200

    data = response.get_json()

    assert "message" in data
    assert "API key regenerated successfully" in data["message"]

@patch("app.routes.admin.admin_nightline_routes.Nightline.renew_api_key")
def test_renew_nightline_api_key_not_found_api_key(mock_renew_api_key, client, headers_with_valid_token):
    mock_renew_api_key.return_value = None

    response = client.patch("/admin/nightline/key/testline", headers=headers_with_valid_token)

    assert response.status_code == 500

    data = response.get_json()
    assert "message" in data
    assert "No api key found for nightline: 'testline'" in data["message"]

    Nightline.remove_nightline("testline")

def test_renew_nightline_api_key_nightline_not_found(client, headers_with_valid_token):
    response = client.patch("/admin/nightline/key/testline", headers=headers_with_valid_token)

    assert response.status_code == 404

    data = response.get_json()
    assert "message" in data
    assert "Nightline 'testline' not found" in data["message"]
