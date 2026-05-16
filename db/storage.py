import os
import sqlite3


def init_db(db_path: str) -> None:
    dir_path = os.path.dirname(db_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id    INTEGER PRIMARY KEY,
                language   TEXT NOT NULL DEFAULT 'en',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()


def get_language(user_id: int, db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT language FROM user_settings WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row[0] if row else "en"
    finally:
        conn.close()


def set_language(user_id: int, lang_code: str, db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            INSERT INTO user_settings (user_id, language, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                language = excluded.language,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, lang_code))
        conn.commit()
    finally:
        conn.close()
