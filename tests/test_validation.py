from io import BytesIO
from unittest.mock import patch

import pytest
from werkzeug.datastructures import FileStorage

from app.validation import (
    validate_filters,
    validate_image,
    validate_instagram_credentials,
    validate_request_body,
    validate_status_value,
)


# -------------------------
# validate_request_body
# -------------------------
def test_validate_request_body_valid():
    assert validate_request_body({"key1": "value"}, ["key1"]) is True


def test_validate_request_body_missing_one_key():
    with patch("app.validation.abort") as mock_abort:
        validate_request_body({"key1": "value"}, ["key1", "key2"])
        mock_abort.assert_called_once_with(400, "Missing 'key2' in request")


def test_validate_request_body_missing_multiple_keys():
    with patch("app.validation.abort") as mock_abort:
        validate_request_body({"key1": "value"}, ["key1", "key2", "key3"])
        mock_abort.assert_called_once_with(400, "Missing 'key2' or 'key3' in request")


def test_validate_request_body_no_keys():
    assert validate_request_body({"anything": "value"}, []) is False


# -------------------------
# validate_filters
# -------------------------
@pytest.mark.parametrize("status", ["valid123", None])
@pytest.mark.parametrize("language", ["de", None])
@pytest.mark.parametrize("now", ["true", None])
def test_validate_filters_valid(status, language, now):
    assert (
        validate_filters(status_filter=status, language_filter=language, now_filter=now)
        is None
    )


@pytest.mark.parametrize("status", ["invalid!", "a" * 16, 123])
def test_validate_filters_invalid_status(status):
    with patch("app.validation.abort") as mock_abort:
        validate_filters(status_filter=status)
        mock_abort.assert_called_once()


def test_validate_filters_invalid_language():
    with patch("app.validation.abort") as mock_abort:
        validate_filters(language_filter="fr")
        mock_abort.assert_called_once()


def test_validate_filters_invalid_now():
    with patch("app.validation.abort") as mock_abort:
        validate_filters(now_filter="maybe")
        mock_abort.assert_called_once()


# -------------------------
# validate_status_value
# -------------------------
def test_validate_status_value_valid():
    assert validate_status_value("open") is None


@pytest.mark.parametrize("status", ["", "a" * 16, 123])
def test_validate_status_value_invalid(status):
    with patch("app.validation.abort") as mock_abort:
        validate_status_value(status)
        mock_abort.assert_called_once()


# -------------------------
# validate_instagram_credentials
# -------------------------
def test_validate_instagram_credentials_valid():
    assert validate_instagram_credentials("user", "pass") is None


def test_validate_instagram_credentials_invalid():
    with patch("app.validation.abort") as mock_abort:
        validate_instagram_credentials("a" * 51, "pass")
        mock_abort.assert_called_once()

    with patch("app.validation.abort") as mock_abort:
        validate_instagram_credentials("user", "b" * 101)
        mock_abort.assert_called_once()


# -------------------------
# validate_image
# -------------------------
def test_validate_image_valid():
    img_data = BytesIO()
    Image = pytest.importorskip("PIL.Image")
    image = Image.new("RGB", (10, 10))
    image.save(img_data, format="PNG")
    img_data.seek(0)
    file = FileStorage(stream=img_data, filename="test.png", content_type="image/png")
    assert validate_image(file) is None


def test_validate_image_unsupported_type():
    file = FileStorage(
        stream=BytesIO(b"not really an image"),
        content_type="text/plain",
        filename="fake.png",
    )
    with patch("app.validation.abort") as mock_abort:
        validate_image(file)
        mock_abort.assert_called_once_with(400, "Unsupported image type")


def test_validate_image_invalid_content():
    file = FileStorage(
        stream=BytesIO(b"not really an image"),
        content_type="image/png",
        filename="fake.png",
    )

    with patch("app.validation.abort") as mock_abort:
        validate_image(file)
        mock_abort.assert_called_once_with(400, "Invalid image content")
