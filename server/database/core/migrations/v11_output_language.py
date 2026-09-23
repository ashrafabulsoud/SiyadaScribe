"""Migration v11: add output language and the transcription language default."""

import json


def migrate(cursor, _db):
    """Preserve the output_language column already present in SiyadaScribe 1.0.5."""
    cursor.execute("PRAGMA table_info(user_settings)")
    if "output_language" not in {row["name"] for row in cursor.fetchall()}:
        cursor.execute("ALTER TABLE user_settings ADD COLUMN output_language TEXT DEFAULT 'auto'")

    cursor.execute(
        "INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)",
        ("WHISPER_LANGUAGE", json.dumps("auto")),
    )
