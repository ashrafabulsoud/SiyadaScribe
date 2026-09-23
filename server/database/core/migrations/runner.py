"""
Migration runner with savepoint-based transaction handling.
"""

import logging

SCHEMA_VERSION = 11


def _is_siyadascribe_105_schema(cursor) -> bool:
    """SiyadaScribe 1.0.5 stamped v6 for its own output_language column, before upstream's v6
    restructured patients into encounters + patient_profiles."""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' "
        "AND name IN ('patients', 'patient_profiles')"
    )
    tables = {row["name"] for row in cursor.fetchall()}
    return "patients" in tables and "patient_profiles" not in tables


def _assign_legacy_ur_numbers(cursor) -> int:
    """Upstream v6 only carries name/dob/gender into patient_profiles for rows with a UR number."""
    cursor.execute(
        "UPDATE patients SET ur_number = 'LEGACY-' || id "
        "WHERE ur_number IS NULL OR trim(ur_number) = ''"
    )
    return cursor.rowcount


def run_migrations(patient_db):
    """Run all pending schema migrations.

    Uses SAVEPOINT so each migration can be rolled back individually
    without discarding the work of prior migrations in the same run. The
    whole run is one locked transaction on the shared connection: commit
    happens once at the end on success, full rollback on any failure.

    Args:
        patient_db: PatientDatabase instance exposing ``transaction()``
    """
    from server.database.core.migrations import MIGRATIONS

    try:
        with patient_db.transaction() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                )
            """
            )

            cursor.execute("SELECT MAX(version) AS version FROM schema_version")
            result = cursor.fetchone()
            current_version = (result["version"] if result else None) or 0

            if current_version == 6 and _is_siyadascribe_105_schema(cursor):
                relabelled = _assign_legacy_ur_numbers(cursor)
                logging.info(
                    "Detected SiyadaScribe 1.0.5 schema; replaying upstream migrations from v6 "
                    f"({relabelled} visits without a UR number were given LEGACY-<id>)."
                )
                current_version = 5

            if current_version < SCHEMA_VERSION:
                logging.info(
                    f"Updating database from version {current_version + 1} to {SCHEMA_VERSION}"
                )

                for version in range(current_version + 1, SCHEMA_VERSION + 1):
                    migration_func = MIGRATIONS.get(version)
                    if not migration_func:
                        raise RuntimeError(f"Missing migration: v{version}")

                    logging.info(f"Running migration to version {version}")

                    cursor.execute(f"SAVEPOINT v{version}")
                    try:
                        migration_func(cursor, patient_db.db)
                    except Exception:
                        cursor.execute(f"ROLLBACK TO SAVEPOINT v{version}")
                        raise

                cursor.execute("DELETE FROM schema_version")
                cursor.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (SCHEMA_VERSION,),
                )

        logging.info(f"Database schema is at version {SCHEMA_VERSION}")

    except Exception as e:
        logging.error(f"Migration failed: {str(e)}")
        raise
