import io
from unittest.mock import patch

import pytest

from app.config import Config
from app.models.nightline import Nightline
from app.models.nightlinestatus import NightlineStatus


@pytest.fixture
def auth_header_admin():
    return {"Authorization": Config.ADMIN_API_KEY, "Content-Type": "application/json"}


@pytest.fixture
def auth_header_needs_key():
    return {"Authorization": "", "Content-Type": "application/json"}


# -------------------------
# require_api_key [decorator]
# -------------------------
def test_set_status_missing_auth_header(client):
    response = client.patch(
        "/nightline/testline/status",
    )

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
    nightline = Nightline.add_nightline("testline")

    headers = {"Authorization": "invalid-key"}

    response = client.patch(f"/nightline/{nightline.name}/status", headers=headers, json={"status": "english"})

    assert response.status_code == 403
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Invalid API key"


# -------------------------
# nightline/<nightline_name>/status [patch]
# -------------------------
def test_set_status_success(client, auth_header_needs_key):
    nightline = Nightline.get_nightline("testline")

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
def test_reset_status_nightline_not_found(client, auth_header_admin):
    response = client.delete(
        "/nightline/invalidnightline/status",
        headers=auth_header_admin,
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Nightline 'invalidnightline' not found"


@patch("app.routes.nightline.nightline_routes.Nightline.reset_status")
def test_reset_status_resetting_failes(mock_reset_status, client, auth_header_admin):
    mock_reset_status.return_value = False

    nightline = Nightline.get_nightline("testline")

    response = client.delete(
        f"/nightline/{nightline.name}/status",
        headers=auth_header_admin,
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Resetting the status failed"


@patch("app.routes.nightline.nightline_routes.Nightline.delete_instagram_story")
def test_reset_status_deleting_instagram_story_fails(mock_delete_instagram_story, client, auth_header_admin):
    mock_delete_instagram_story.return_value = False

    nightline = Nightline.get_nightline("testline")
    nightline.set_instagram_media_id("exampleID")

    response = client.delete(
        f"/nightline/{nightline.name}/status",
        headers=auth_header_admin,
    )

    assert response.status_code == 500
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Staus successfully reset but deleting the current instagram story failed"


@patch("app.routes.nightline.nightline_routes.Nightline.delete_instagram_story")
def test_reset_status_success(mock_delete_instagram_story, client, auth_header_admin):
    mock_delete_instagram_story.return_value = True

    nightline = Nightline.get_nightline("testline")

    response = client.delete(
        f"/nightline/{nightline.name}/status",
        headers=auth_header_admin,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Status successfully reset to: 'default'"


# -------------------------
# nightline/<nightline_name>/status/config [patch]
# -------------------------
def test_configure_nightline_status_success(client, auth_header_admin):
    data = {"status": "english", "instagram_story": False}

    response = client.patch("/nightline/testline/status/config", headers=auth_header_admin, json=data)

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Status successfully updated"


def test_configure_nightline_status_invalid_data(client, auth_header_admin):
    data = {"status": "string", "instagram_story": "False"}

    response = client.patch("/nightline/invalidnightline/status/config", headers=auth_header_admin, json=data)

    assert response.status_code == 400
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"'instagram_story' must be a boolean"


def test_configure_nightline_status_nightline_not_found(client, auth_header_admin):
    data = {"status": "string", "instagram_story": False}

    response = client.patch("/nightline/invalidnightline/status/config", headers=auth_header_admin, json=data)

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Nightline 'invalidnightline' not found"


def test_configure_nightline_status_invalid_status(client, auth_header_admin):
    data = {"status": "unknown", "instagram_story": False}

    response = client.patch("/nightline/testline/status/config", headers=auth_header_admin, json=data)

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Status 'unknown' not found"


@patch("app.routes.nightline.nightline_routes.NightlineStatus.get_nightline_status")
def test_configure_nightline_status_nightline_status_not_found(mock_get_nightline_status, client, auth_header_admin):
    mock_get_nightline_status.return_value = False

    data = {"status": "english", "instagram_story": False}

    response = client.patch("/nightline/testline/status/config", headers=auth_header_admin, json=data)

    assert response.status_code == 500
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Status 'english' for nightline 'testline' not found"


def test_configure_nightline_status_no_story_slide_configured(client, auth_header_admin):
    data = {"status": "english", "instagram_story": True}

    response = client.patch("/nightline/testline/status/config", headers=auth_header_admin, json=data)

    assert response.status_code == 400
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"No story slide set for status 'english' of nightline 'testline'"


@patch("app.routes.nightline.nightline_routes.NightlineStatus.update_instagram_story")
def test_configure_nightline_status_update_instagram_story_fails(mock_update_instagram_story, client, auth_header_admin):
    mock_update_instagram_story.return_value = False

    data = {"status": "english", "instagram_story": False}

    response = client.patch("/nightline/testline/status/config", headers=auth_header_admin, json=data)

    assert response.status_code == 500
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Updating the status failed"


# -------------------------
# nightline/<nightline_name>/now [patch]
# -------------------------
def test_update_now_success(client, auth_header_admin):
    response = client.patch("/nightline/testline/now", headers=auth_header_admin, json={"now": True})

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Now value successfully set to 'True'"


def test_update_now_invalid_data(client, auth_header_admin):
    response = client.patch("/nightline/testline/now", headers=auth_header_admin, json={"now": "True"})

    assert response.status_code == 400
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"'now' must be a boolean"


def test_update_now_nightline_not_found(client, auth_header_admin):
    response = client.patch("/nightline/invalidnightline/now", headers=auth_header_admin, json={"now": True})

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Nightline 'invalidnightline' not found"


# -------------------------
# nightline/<nightline_name>/instagram [post]
# -------------------------
def test_add_instagram_acc_success(client, auth_header_admin):
    response = client.post("/nightline/testline/instagram", headers=auth_header_admin, json={"username": "testuser", "password": "testpw"})

    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Instagram account added successfully"


def test_add_instagram_acc_nightline_not_found(client, auth_header_admin):
    response = client.post("/nightline/invalidnightline/instagram", headers=auth_header_admin, json={"username": "testuser", "password": "testpw"})

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Nightline 'invalidnightline' not found"


def test_add_instagram_acc_already_existing(client, auth_header_admin):
    response = client.post("/nightline/testline/instagram", headers=auth_header_admin, json={"username": "testuser", "password": "testpw"})

    assert response.status_code == 400
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"There already exists an Instagram account for this nightline"


# -------------------------
# nightline/<nightline_name>/instagram [patch]
# -------------------------
def test_update_instagram_creds_success(client, auth_header_admin):
    response = client.patch("/nightline/testline/instagram", headers=auth_header_admin, json={"username": "testuser", "password": "testpw"})

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Instagram account data updated successfully"


def test_update_instagram_creds_nightline_not_found(client, auth_header_admin):
    response = client.patch("/nightline/invalidnightline/instagram", headers=auth_header_admin, json={"username": "testuser", "password": "testpw"})

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Nightline 'invalidnightline' not found"


def test_update_instagram_creds_nightline_missing_insta_acc(client, auth_header_admin):
    nightline = Nightline.get_nightline("testline")
    nightline.delete_instagram_account()

    response = client.patch(f"/nightline/{nightline.name}/instagram", headers=auth_header_admin, json={"username": "testuser", "password": "testpw"})

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Instagram account not found for this nightline"


# -------------------------
# nightline/<nightline_name>/instagram [delete]
# -------------------------
def test_delete_instagram_account_success(client, auth_header_admin):
    nightline = Nightline.get_nightline("testline")
    nightline.add_instagram_account("testuser", "testpw")

    response = client.delete(
        f"/nightline/{nightline.name}/instagram",
        headers=auth_header_admin,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Instagram account deleted successfully"


def test_delete_instagram_account_nightline_not_found(client, auth_header_admin):
    response = client.delete(
        "/nightline/invalidnightline/instagram",
        headers=auth_header_admin,
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Nightline 'invalidnightline' not found"


def test_delete_instagram_account_already_deleted(client, auth_header_admin):
    response = client.delete(
        "/nightline/testline/instagram",
        headers=auth_header_admin,
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "message" in data
    assert data["message"] == f"Instagram account not found for this nightline"


# -------------------------
# nightline/<nightline_name>/story [post]
# -------------------------
@patch("app.routes.nightline.nightline_routes.validate_image")
def test_upload_story_slide_success(mock_validate_image, client, auth_header_admin):
    mock_validate_image.return_value = True

    nightline_name = "testline"
    status_name = "english"

    image_data = io.BytesIO(b"\xff\xd8\xff\xe0" + b"FakeJPEGContent")
    image_data.name = "test.jpg"

    data = {"status": status_name, "image": (image_data, image_data.name)}

    response = client.post(f"/nightline/{nightline_name}/story", headers=auth_header_admin, content_type="multipart/form-data", data=data)

    assert response.status_code == 201
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Story for status '{status_name}' added successfully" in res_json["message"]


@patch("app.routes.nightline.nightline_routes.validate_image")
def test_upload_story_slide_nightline_not_found(mock_validate_image, client, auth_header_admin):
    mock_validate_image.return_value = True

    nightline_name = "invalidnightline"
    status_name = "english"

    image_data = io.BytesIO(b"\xff\xd8\xff\xe0" + b"FakeJPEGContent")
    image_data.name = "test.jpg"

    data = {"status": status_name, "image": (image_data, image_data.name)}

    response = client.post(f"/nightline/{nightline_name}/story", headers=auth_header_admin, content_type="multipart/form-data", data=data)

    assert response.status_code == 404
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Nightline 'invalidnightline' not found" in res_json["message"]


@patch("app.routes.nightline.nightline_routes.validate_image")
def test_upload_story_slide_status_not_found(mock_validate_image, client, auth_header_admin):
    mock_validate_image.return_value = True

    nightline_name = "testline"
    status_name = "unknown"

    image_data = io.BytesIO(b"\xff\xd8\xff\xe0" + b"FakeJPEGContent")
    image_data.name = "test.jpg"

    data = {"status": status_name, "image": (image_data, image_data.name)}

    response = client.post(f"/nightline/{nightline_name}/story", headers=auth_header_admin, content_type="multipart/form-data", data=data)

    assert response.status_code == 404
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Status '{status_name}' not found" in res_json["message"]


@patch("app.routes.nightline.nightline_routes.validate_image")
@patch("app.routes.nightline.nightline_routes.NightlineStatus.get_nightline_status")
def test_upload_story_slide_nightline_status_not_found(mock_get_nightline_status, mock_validate_image, client, auth_header_admin):
    mock_validate_image.return_value = True
    mock_get_nightline_status.return_value = False

    nightline_name = "testline"
    status_name = "english"

    image_data = io.BytesIO(b"\xff\xd8\xff\xe0" + b"FakeJPEGContent")
    image_data.name = "test.jpg"

    data = {"status": status_name, "image": (image_data, image_data.name)}

    response = client.post(f"/nightline/{nightline_name}/story", headers=auth_header_admin, content_type="multipart/form-data", data=data)

    assert response.status_code == 404
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Status '{status_name}' not found" in res_json["message"]


@patch("app.routes.nightline.nightline_routes.validate_image")
@patch("app.routes.nightline.nightline_routes.StorySlide.update_story_slide")
def test_upload_story_slide_update_story_slide_fails(mock_update_story_slide, mock_validate_image, client, auth_header_admin):
    mock_validate_image.return_value = True
    mock_update_story_slide.return_value = False

    nightline_name = "testline"
    status_name = "english"

    image_data = io.BytesIO(b"\xff\xd8\xff\xe0" + b"FakeJPEGContent")
    image_data.name = "test.jpg"

    data = {"status": status_name, "image": (image_data, image_data.name)}

    response = client.post(f"/nightline/{nightline_name}/story", headers=auth_header_admin, content_type="multipart/form-data", data=data)

    assert response.status_code == 500
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Uploading a story slide for status 'english' failed" in res_json["message"]


# -------------------------
# nightline/<nightline_name>/story [delete]
# -------------------------
def test_remove_story_slide_success(client, auth_header_admin):
    nightline_name = "testline"
    status_name = "english"

    response = client.delete(
        f"/nightline/{nightline_name}/story",
        headers=auth_header_admin,
        json={
            "status": status_name,
        },
    )

    assert response.status_code == 200
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Story for status '{status_name}' removed successfully" in res_json["message"]


def test_remove_story_slide_nightline_not_found(client, auth_header_admin):
    nightline_name = "invalidnightline"
    status_name = "english"

    response = client.delete(f"/nightline/{nightline_name}/story", headers=auth_header_admin, json={"status": status_name})

    assert response.status_code == 404
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Nightline '{nightline_name}' not found" in res_json["message"]


def test_remove_story_slide_status_not_found(client, auth_header_admin):
    nightline_name = "testline"
    status_name = "unknown"

    response = client.delete(f"/nightline/{nightline_name}/story", headers=auth_header_admin, json={"status": status_name})

    assert response.status_code == 404
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Status '{status_name}' not found" in res_json["message"]


@patch("app.routes.nightline.nightline_routes.NightlineStatus.get_nightline_status")
def test_remove_story_slide_nightline_status_not_found(mock_get_nightline_status, client, auth_header_admin):
    mock_get_nightline_status.return_value = False

    nightline_name = "testline"
    status_name = "english"

    response = client.delete(f"/nightline/{nightline_name}/story", headers=auth_header_admin, json={"status": status_name})

    assert response.status_code == 404
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Status '{status_name}' not found" in res_json["message"]


@patch("app.routes.nightline.nightline_routes.StorySlide.remove_story_slide")
def test_remove_story_slide_removing_fails(mock_remove_story_slide, client, auth_header_admin):
    mock_remove_story_slide.return_value = False

    nightline_name = "testline"
    status_name = "english"

    response = client.delete(f"/nightline/{nightline_name}/story", headers=auth_header_admin, json={"status": status_name})

    assert response.status_code == 500
    res_json = response.get_json()
    assert "message" in res_json
    assert f"Deleting a story slide for status '{status_name}' failed" in res_json["message"]
