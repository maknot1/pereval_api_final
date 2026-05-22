import os
from copy import deepcopy

import pytest

from app.config import get_database_config
from app.database import DatabaseManager
from tests.test_api import VALID_PAYLOAD


def test_database_config_reads_environment(monkeypatch):
    monkeypatch.setenv("FSTR_DB_HOST", "127.0.0.1")
    monkeypatch.setenv("FSTR_DB_PORT", "5433")
    monkeypatch.setenv("FSTR_DB_NAME", "test_pereval_db")
    monkeypatch.setenv("FSTR_DB_LOGIN", "test_user")
    monkeypatch.setenv("FSTR_DB_PASS", "test_password")

    config = get_database_config()

    assert config.host == "127.0.0.1"
    assert config.port == 5433
    assert config.database == "test_pereval_db"
    assert config.login == "test_user"
    assert config.password == "test_password"


@pytest.mark.skipif(
    os.getenv("FSTR_TEST_DB") != "1",
    reason="Set FSTR_TEST_DB=1 and configure PostgreSQL env vars to run DB integration test.",
)
def test_database_manager_crud_integration():
    database = DatabaseManager()
    payload = deepcopy(VALID_PAYLOAD)
    payload["user"]["email"] = "db-test@example.com"

    pereval_id = database.add_pereval(payload)
    created = database.get_pereval_by_id(pereval_id)

    assert created is not None
    assert created["id"] == pereval_id
    assert created["status"] == "new"
    assert created["title"] == payload["title"]

    payload["title"] = "Обновленный перевал"
    update_result = database.update_pereval(pereval_id, payload)
    assert update_result["state"] == 1

    updated = database.get_pereval_by_id(pereval_id)
    assert updated["title"] == "Обновленный перевал"

    by_email = database.get_perevals_by_email("db-test@example.com")
    assert any(item["id"] == pereval_id for item in by_email)
