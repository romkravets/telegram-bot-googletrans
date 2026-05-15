import tempfile
import os
from db.storage import init_db, get_language, set_language

def make_db():
    tmp = tempfile.mktemp(suffix=".db")
    init_db(tmp)
    return tmp

def test_default_language_is_en():
    db = make_db()
    assert get_language(123, db) == "en"
    os.unlink(db)

def test_set_and_get_language():
    db = make_db()
    set_language(123, "uk", db)
    assert get_language(123, db) == "uk"
    os.unlink(db)

def test_update_existing_language():
    db = make_db()
    set_language(123, "uk", db)
    set_language(123, "de", db)
    assert get_language(123, db) == "de"
    os.unlink(db)

def test_different_users_are_independent():
    db = make_db()
    set_language(1, "uk", db)
    set_language(2, "fr", db)
    assert get_language(1, db) == "uk"
    assert get_language(2, db) == "fr"
    os.unlink(db)
