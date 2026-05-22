from copy import deepcopy

from fastapi.testclient import TestClient

from app.main import app, get_database


VALID_PAYLOAD = {
    "beauty_title": "пер.",
    "title": "Пхия",
    "other_titles": "Триев",
    "connect": "",
    "add_time": "2026-05-22T12:00:00",
    "user": {
        "email": "tourist@example.com",
        "fam": "Иванов",
        "name": "Иван",
        "otc": "Иванович",
        "phone": "+79999999999",
    },
    "coords": {
        "latitude": 45.3842,
        "longitude": 7.1525,
        "height": 1200,
    },
    "level": {
        "winter": "",
        "summer": "1А",
        "autumn": "1А",
        "spring": "",
    },
    "images": [
        {
            "data": "base64_or_url_1",
            "title": "Фото перевала 1",
        }
    ],
}


class FakeDatabase:
    def __init__(self) -> None:
        self.items = {}
        self.next_id = 1

    def add_pereval(self, data):
        pereval_id = self.next_id
        self.next_id += 1
        item = deepcopy(data)
        item["id"] = pereval_id
        item["status"] = "new"
        self.items[pereval_id] = item
        return pereval_id

    def get_pereval_by_id(self, pereval_id):
        return self.items.get(pereval_id)

    def update_pereval(self, pereval_id, data):
        item = self.items.get(pereval_id)
        if item is None:
            return {"state": 0, "message": "Запись не найдена"}
        if item["status"] != "new":
            return {
                "state": 0,
                "message": "Редактирование запрещено: статус записи не new",
            }
        original_user = item["user"]
        updated = deepcopy(data)
        updated["id"] = pereval_id
        updated["status"] = "new"
        updated["user"] = original_user
        self.items[pereval_id] = updated
        return {"state": 1, "message": "Запись успешно обновлена"}

    def get_perevals_by_email(self, email):
        return [
            item for item in self.items.values()
            if item["user"]["email"].lower() == email.lower()
        ]


def create_test_client():
    fake_database = FakeDatabase()
    app.dependency_overrides[get_database] = lambda: fake_database
    return TestClient(app), fake_database


def test_post_submit_data_success():
    client, _ = create_test_client()

    response = client.post("/submitData", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.json() == {
        "status": 200,
        "message": "Отправлено успешно",
        "id": 1,
    }

    app.dependency_overrides.clear()


def test_post_submit_data_bad_request():
    client, _ = create_test_client()
    invalid_payload = deepcopy(VALID_PAYLOAD)
    invalid_payload.pop("title")

    response = client.post("/submitData", json=invalid_payload)

    assert response.status_code == 400
    assert response.json()["status"] == 400

    app.dependency_overrides.clear()


def test_get_submit_data_by_id_success():
    client, _ = create_test_client()
    post_response = client.post("/submitData", json=VALID_PAYLOAD)
    pereval_id = post_response.json()["id"]

    response = client.get(f"/submitData/{pereval_id}")

    assert response.status_code == 200
    assert response.json()["id"] == pereval_id
    assert response.json()["status"] == "new"
    assert response.json()["title"] == "Пхия"

    app.dependency_overrides.clear()


def test_get_submit_data_by_id_not_found():
    client, _ = create_test_client()

    response = client.get("/submitData/999")

    assert response.status_code == 404
    assert response.json()["message"] == "Запись не найдена"

    app.dependency_overrides.clear()


def test_patch_submit_data_success_and_preserves_user():
    client, fake_database = create_test_client()
    post_response = client.post("/submitData", json=VALID_PAYLOAD)
    pereval_id = post_response.json()["id"]

    new_payload = deepcopy(VALID_PAYLOAD)
    new_payload["title"] = "Новый перевал"
    new_payload["user"] = {
        "email": "changed@example.com",
        "fam": "Петров",
        "name": "Петр",
        "otc": "Петрович",
        "phone": "+78888888888",
    }

    response = client.patch(f"/submitData/{pereval_id}", json=new_payload)

    assert response.status_code == 200
    assert response.json() == {"state": 1, "message": "Запись успешно обновлена"}
    assert fake_database.items[pereval_id]["title"] == "Новый перевал"
    assert fake_database.items[pereval_id]["user"]["email"] == "tourist@example.com"

    app.dependency_overrides.clear()


def test_patch_submit_data_forbidden_when_status_is_not_new():
    client, fake_database = create_test_client()
    post_response = client.post("/submitData", json=VALID_PAYLOAD)
    pereval_id = post_response.json()["id"]
    fake_database.items[pereval_id]["status"] = "accepted"

    response = client.patch(f"/submitData/{pereval_id}", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["state"] == 0

    app.dependency_overrides.clear()


def test_get_submit_data_by_email():
    client, _ = create_test_client()
    client.post("/submitData", json=VALID_PAYLOAD)

    response = client.get("/submitData/?user__email=tourist@example.com")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user"]["email"] == "tourist@example.com"

    app.dependency_overrides.clear()
