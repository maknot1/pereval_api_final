# FSTR Pereval REST API

REST API для передачи данных о горных перевалах в Федерацию спортивного туризма России. Проект сделан для задания SkillFactory по виртуальной стажировке.

## Стек

- Python 3.12
- FastAPI
- PostgreSQL
- psycopg
- Pydantic
- pytest
- Swagger / OpenAPI
- Docker Compose для локальной базы данных

## Реализованные методы

| Метод | URL | Назначение |
|---|---|---|
| POST | `/submitData` | Добавить новый перевал |
| GET | `/submitData/{id}` | Получить перевал по id |
| PATCH | `/submitData/{id}` | Отредактировать перевал, если его статус `new` |
| GET | `/submitData/?user__email=<email>` | Получить все перевалы пользователя по email |

## Структура проекта

```text
pereval_api_submission/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── schemas.py
├── db/
│   └── schema.sql
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_database.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## Быстрый запуск

### 1. Создать виртуальное окружение

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Запустить PostgreSQL через Docker Compose

```bash
docker compose up -d
```

При первом запуске Docker сам создаст таблицы из файла:

```text
db/schema.sql
```

### 4. Создать `.env`

Можно скопировать пример:

```bash
cp .env.example .env
```

Для Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Содержимое `.env.example`:

```env
FSTR_DB_HOST=localhost
FSTR_DB_PORT=5432
FSTR_DB_NAME=pereval_db
FSTR_DB_LOGIN=pereval_user
FSTR_DB_PASS=pereval_pass
```

В задании есть расхождение в названиях переменных. В основной части указаны `FSTR_DB_LOGIN` и `FSTR_DB_PASS`, а в критериях встречаются `FSTR_LOGIN` и `FSTR_PASS`. Проект поддерживает оба варианта.

### 5. Запустить API

```bash
uvicorn app.main:app --reload
```

API будет доступен по адресу:

```text
http://127.0.0.1:8000
```

Swagger-документация:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

## База данных

В проекте используется переработанная структура базы данных:

- `users` - данные пользователя;
- `coords` - координаты и высота перевала;
- `levels` - уровни сложности по сезонам;
- `perevals` - основная таблица перевалов;
- `images` - фотографии перевалов.

В таблицу `perevals` добавлено обязательное поле:

```text
status
```

Допустимые значения:

```text
new
pending
accepted
rejected
```

При добавлении нового перевала через `POST /submitData` статус автоматически устанавливается как:

```text
new
```

## Примеры запросов

### POST /submitData

```bash
curl -X POST http://127.0.0.1:8000/submitData \
-H "Content-Type: application/json" \
-d '{
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
    "phone": "+79999999999"
  },
  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525,
    "height": 1200
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {
      "data": "base64_or_url_1",
      "title": "Фото перевала 1"
    }
  ]
}'
```

Успешный ответ:

```json
{
  "status": 200,
  "message": "Отправлено успешно",
  "id": 1
}
```

Ошибка валидации:

```json
{
  "status": 400,
  "message": "Bad Request: не хватает или неверно заполнены поля"
}
```

Ошибка сервера:

```json
{
  "status": 500,
  "message": "Описание ошибки"
}
```

### GET /submitData/{id}

```bash
curl http://127.0.0.1:8000/submitData/1
```

Пример ответа:

```json
{
  "id": 1,
  "beauty_title": "пер.",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2026-05-22T12:00:00",
  "status": "new",
  "user": {
    "email": "tourist@example.com",
    "fam": "Иванов",
    "name": "Иван",
    "otc": "Иванович",
    "phone": "+79999999999"
  },
  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525,
    "height": 1200
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {
      "data": "base64_or_url_1",
      "title": "Фото перевала 1"
    }
  ]
}
```

### PATCH /submitData/{id}

Метод принимает такой же JSON, как `POST /submitData`.

Редактировать можно только записи со статусом:

```text
new
```

Данные пользователя не редактируются:

- фамилия;
- имя;
- отчество;
- email;
- телефон.

Пример:

```bash
curl -X PATCH http://127.0.0.1:8000/submitData/1 \
-H "Content-Type: application/json" \
-d '{
  "beauty_title": "пер.",
  "title": "Пхия обновленная",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2026-05-22T12:00:00",
  "user": {
    "email": "another@example.com",
    "fam": "Петров",
    "name": "Петр",
    "otc": "Петрович",
    "phone": "+78888888888"
  },
  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525,
    "height": 1300
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {
      "data": "base64_or_url_2",
      "title": "Новое фото"
    }
  ]
}'
```

Успешный ответ:

```json
{
  "state": 1,
  "message": "Запись успешно обновлена"
}
```

Если статус не `new`:

```json
{
  "state": 0,
  "message": "Редактирование запрещено: статус записи не new"
}
```

### GET /submitData/?user__email=<email>

```bash
curl "http://127.0.0.1:8000/submitData/?user__email=tourist@example.com"
```

Пример ответа:

```json
[
  {
    "id": 1,
    "beauty_title": "пер.",
    "title": "Пхия",
    "other_titles": "Триев",
    "connect": "",
    "add_time": "2026-05-22T12:00:00",
    "status": "new",
    "user": {
      "email": "tourist@example.com",
      "fam": "Иванов",
      "name": "Иван",
      "otc": "Иванович",
      "phone": "+79999999999"
    },
    "coords": {
      "latitude": 45.3842,
      "longitude": 7.1525,
      "height": 1200
    },
    "level": {
      "winter": "",
      "summer": "1А",
      "autumn": "1А",
      "spring": ""
    },
    "images": [
      {
        "data": "base64_or_url_1",
        "title": "Фото перевала 1"
      }
    ]
  }
]
```

## Тесты

Запуск тестов:

```bash
pytest
```

В проекте есть:

- тесты REST API через `TestClient`;
- тест чтения переменных окружения;
- интеграционный тест класса `DatabaseManager` для PostgreSQL.

Интеграционный тест БД по умолчанию пропущен, чтобы обычный `pytest` проходил без локальной PostgreSQL-базы. Чтобы запустить его, нужно поднять базу и указать переменную:

Linux / macOS:

```bash
export FSTR_TEST_DB=1
pytest tests/test_database.py
```

Windows PowerShell:

```powershell
$env:FSTR_TEST_DB="1"
pytest tests/test_database.py
```

## Git

Рекомендуемый порядок коммитов:

```bash
git init
git checkout -b feature/pereval-api
git add .
git commit -m "Initial project structure"
git commit -m "Add database schema and config"
git commit -m "Implement submitData API endpoints"
git commit -m "Add tests and documentation"
git checkout master
git merge feature/pereval-api
```

## Что закрывает критерии задания

| Критерий | Статус |
|---|---|
| Класс для работы с БД | Выполнено |
| REST API, спринт 1: POST /submitData | Выполнено |
| REST API, спринт 2: GET, PATCH, GET by email | Выполнено |
| README.md | Выполнено |
| Code style | Выполнено |
| Переменные окружения | Выполнено |
| Переработанная структура БД | Выполнено |
| Swagger | Выполнено через FastAPI `/docs` |
| Тесты | Выполнено |
| Git | Нужно сделать коммиты в своём репозитории |
