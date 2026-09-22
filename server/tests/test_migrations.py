"""Replay migrations against real scratch SQLCipher databases."""

import pytest
import sqlcipher3 as sqlite3

from server.database.core.connection import PatientDatabase
from server.database.core.migrations import MIGRATIONS, run_migrations
from server.database.core.migrations.runner import SCHEMA_VERSION


@pytest.mark.parametrize("legacy_fork", [True, False])
def test_version_six_upgrade(tmp_path, monkeypatch, legacy_fork):
    monkeypatch.setenv("TESTING", "true")
    path = tmp_path / "test_siyadascribe_database.sqlite"
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.cursor()
        cursor.execute("PRAGMA key='migration-test-key'")
        cursor.execute("CREATE TABLE schema_version (version INTEGER PRIMARY KEY)")
        for version in range(1, 6 if legacy_fork else 7):
            MIGRATIONS[version](cursor, connection)
        if legacy_fork:
            cursor.execute(
                "ALTER TABLE user_settings ADD COLUMN output_language TEXT DEFAULT 'auto'"
            )
            cursor.execute("INSERT INTO user_settings (output_language) VALUES ('arabic')")
            cursor.executemany(
                "INSERT INTO patients (name, dob, gender, ur_number) VALUES (?, ?, ?, ?)",
                [
                    ("Doe, Jane", "1980-01-02", "F", "UR123"),
                    ("Bob Smith", "1975-05-06", "M", None),
                    ("Madonna", "1990-07-08", "F", "  "),
                ],
            )
        cursor.execute("DELETE FROM config WHERE key = 'WHISPER_LANGUAGE'")
        cursor.execute("INSERT INTO schema_version VALUES (6)")
        connection.commit()
    finally:
        connection.close()

    with PatientDatabase(passphrase="migration-test-key", db_dir=tmp_path) as db:
        # Initialization runs the migration chain; a repeat must be harmless.
        run_migrations(db)
        with db.read() as cursor:
            assert (
                cursor.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
                == SCHEMA_VERSION
            )
            assert (
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='patient_profiles'"
                ).fetchone()
                is not None
            )
            columns = [
                row["name"] for row in cursor.execute("PRAGMA table_info(user_settings)").fetchall()
            ]
            assert columns.count("output_language") == 1
            if legacy_fork:
                assert (
                    cursor.execute("SELECT output_language FROM user_settings").fetchone()[0]
                    == "arabic"
                )
                profiles = cursor.execute(
                    "SELECT ur_number, first_name, last_name, dob, gender FROM patient_profiles "
                    "ORDER BY ur_number"
                ).fetchall()
                assert [tuple(row) for row in profiles] == [
                    ("LEGACY-2", "Bob", "Smith", "1975-05-06", "M"),
                    ("LEGACY-3", "", "Madonna", "1990-07-08", "F"),
                    ("UR123", "Jane", "Doe", "1980-01-02", "F"),
                ]
                encounter_urs = cursor.execute(
                    "SELECT ur_number FROM encounters ORDER BY id"
                ).fetchall()
                assert [row[0] for row in encounter_urs] == ["UR123", "LEGACY-2", "LEGACY-3"]


def test_full_migration_chain_from_empty_database(tmp_path, monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    with (
        PatientDatabase(passphrase="migration-test-key", db_dir=tmp_path) as db,
        db.read() as cursor,
    ):
        assert (
            cursor.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
            == SCHEMA_VERSION
        )
        columns = [
            row["name"] for row in cursor.execute("PRAGMA table_info(user_settings)").fetchall()
        ]
        assert columns.count("output_language") == 1
