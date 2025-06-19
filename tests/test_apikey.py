import re
import pytest
from app.models.apikey import ApiKey
from app.db import db



# -------------------------
# generate_api_key
# -------------------------
def test_generate_api_key_default_length():
    key = ApiKey.generate_api_key()
    assert isinstance(key, str)
    assert len(key) >= 256
    assert re.match(r'^[A-Za-z0-9\-_]+$', key) # check base 64 safety

def test_generate_api_key_custom_length():
    key = ApiKey.generate_api_key(128)
    assert len(key) >= 128

def test_generate_api_key_uniqueness():
    keys = {ApiKey.generate_api_key() for _ in range(50)}
    assert len(keys) == 50  # no duplicates


# -------------------------
# get_api_key
# -------------------------
def test_get_api_key_nonexistent(app):
    result = ApiKey.get_api_key(99999)  # No Nightline with this ID
    assert result is None

def test_api_key_repr():
    api_key = ApiKey(id=42)
    assert repr(api_key) == "ApiKey('42')"

def test_get_api_key_existing(app):
    from app.models.nightline import Nightline

    # Setup Nightline und ApiKey
    nightline = Nightline.add_nightline(name="Testline")
    db.session.add(nightline)
    db.session.commit()

    key = nightline.get_api_key()
    assert key is not None
    assert isinstance(key, ApiKey)
    assert isinstance(key.key, str)
    assert key.nightline_id == nightline.id