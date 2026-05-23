"""Application configuration.

The project task requires database connection settings to be read from
operating system environment variables. FSTR_DB_LOGIN/FSTR_DB_PASS are the
main variables. FSTR_LOGIN/FSTR_PASS are also supported because some versions
of the SkillFactory task mention these names in the evaluation criteria.

For deployment platforms such as Render, DATABASE_URL is also supported.
"""

from dataclasses import dataclass
import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - used only when python-dotenv is absent
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    database: str
    login: str
    password: str
    database_url: str | None = None


def get_database_config() -> DatabaseConfig:
    """Return PostgreSQL connection settings from environment variables."""

    return DatabaseConfig(
        host=os.getenv("FSTR_DB_HOST", "localhost"),
        port=int(os.getenv("FSTR_DB_PORT", "5432")),
        database=os.getenv("FSTR_DB_NAME", "pereval_db"),
        login=os.getenv("FSTR_DB_LOGIN") or os.getenv("FSTR_LOGIN", "pereval_user"),
        password=os.getenv("FSTR_DB_PASS") or os.getenv("FSTR_PASS", "pereval_pass"),
        database_url=os.getenv("DATABASE_URL"),
    )
