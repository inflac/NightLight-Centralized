from unittest.mock import patch

import pytest
import base64
from sqlalchemy.exc import SQLAlchemyError

from cryptography.fernet import Fernet

from app.models.instagram import InstagramAccount

# -------------------------
# validate_file_extension
# -------------------------
def test_derive_key_returns_fernet_instance():
    insta = InstagramAccount()

    example_salt = base64.urlsafe_b64encode(b"1234567890123456").decode()
    insta.salt = example_salt

    fernet = insta.derive_key()
    assert isinstance(fernet, Fernet) # Check if derive_key returns a valid Fernet instance

    # Check if key can be used for enc/dec
    secret_message = b"hello"
    token = fernet.encrypt(secret_message)
    decrypted = fernet.decrypt(token)
    assert decrypted == secret_message


# -------------------------
# validate_file_extension
# -------------------------
def test_set_username_successful():
    acc = InstagramAccount()
    assert acc.set_username("test") is True

@patch("app.models.instagram.logger")
@patch("app.models.instagram.db.session.commit")
def test_set_username_exception(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("DB error")

    acc = InstagramAccount(id=1337)

    result = acc.set_username("test")
    
    assert result is False
    mock_logger.error.assert_called_with(f"Failed to set username for user_id={acc.id}: DB error")


def test_set_password_successfull():
    acc = InstagramAccount(id=418)
    assert acc.set_password("meow") is True


@patch("app.models.instagram.logger")
@patch("app.models.instagram.db.session.commit")
def test_set_password_sqlalchemy_exception(mock_commit, mock_logger):
    mock_commit.side_effect = SQLAlchemyError("DB error")

    acc = InstagramAccount(id=25)
    assert acc.set_password("meow") is False

    mock_logger.error(f"Database error when setting password for user_id={acc.id}: DB error")

@patch("app.models.instagram.logger")
@patch("base64.urlsafe_b64encode")
def test_set_password_general_exception(mock_urlsafe_b64encode, mock_logger):
    mock_urlsafe_b64encode.side_effect = Exception("Exception occured")

    acc = InstagramAccount(id=25)
    assert acc.set_password("meow") is False

    mock_logger.error(f"Unexpected error when setting password for user_id={acc.id}: Exception occured")


def test_get_password_successfull():
    original_password = "superSecret123!"

    insta = InstagramAccount()

    example_salt = base64.urlsafe_b64encode(b"1234567890123456").decode()
    insta.salt = example_salt

    cipher = insta.derive_key()

    # encrypt original password
    insta.encrypted_password = cipher.encrypt(original_password.encode()).decode()

    # Teste get_password decrypts the password correctly
    decrypted_password = insta.get_password()

    assert decrypted_password == original_password


@patch("app.models.instagram.logger.exception")
def test_get_password_exception(mock_logger_exception):
    acc = InstagramAccount(id=42)
    acc.salt = "invalidsalt"  # Invalid base64 to provoke error
    acc.encrypted_password = "not-a-valid-encrypted-password"

    assert acc.get_password() is None

    mock_logger_exception.assert_called_once_with(f"Failed to decrypt password for user_id={acc.id}")