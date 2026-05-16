import tempfile
import os
import pytest
from db.storage import init_db, get_language, set_language


@pytest.fixture
def db_path():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    init_db(path)
    yield path
    os.unlink(path)


def test_default_language_is_en(db_path):
    assert get_language(123, db_path) == "en"


def test_set_and_get_language(db_path):
    set_language(123, "uk", db_path)
    assert get_language(123, db_path) == "uk"


def test_update_existing_language(db_path):
    set_language(123, "uk", db_path)
    set_language(123, "de", db_path)
    assert get_language(123, db_path) == "de"


def test_different_users_are_independent(db_path):
    set_language(1, "uk", db_path)
    set_language(2, "fr", db_path)
    assert get_language(1, db_path) == "uk"
    assert get_language(2, db_path) == "fr"
