"""Initialize PostgreSQL schema before starting the API.

This script is useful for hosted deployments where Docker Compose does not run
and the schema.sql file is not applied automatically.
"""

from pathlib import Path

from app.database import DatabaseManager


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "db" / "schema.sql"


def init_database() -> None:
    """Apply db/schema.sql to the configured PostgreSQL database."""

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    database = DatabaseManager()

    with database._connect() as connection:  # noqa: SLF001 - internal project script
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)
        connection.commit()


if __name__ == "__main__":
    init_database()
    print("Database schema initialized successfully.")
