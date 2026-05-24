# FSTR Pereval REST API

REST API для передачи данных о горных перевалах в Федерацию спортивного туризма России.

## Deployed API

Public API:

```text
https://pereval-api-final.onrender.com
```

Swagger / OpenAPI documentation:

```text
https://pereval-api-final.onrender.com/docs
```

OpenAPI JSON:

```text
https://pereval-api-final.onrender.com/openapi.json
```

Note: the project is deployed on the free Render plan, so the first request after inactivity can take extra time while the service wakes up.

## Stack

- Python 3
- FastAPI
- PostgreSQL
- psycopg
- Pydantic
- pytest
- Swagger / OpenAPI
- Docker Compose for local PostgreSQL
- Render for hosting

## Implemented API methods

| Method | URL | Description |
|---|---|---|
| POST | `/submitData` | Add a new pereval record |
| GET | `/submitData/{id}` | Get one pereval by id |
| PATCH | `/submitData/{id}` | Update a pereval if its status is `new` |
| GET | `/submitData/?user__email=<email>` | Get all perevals submitted by a user email |

## Project structure

```text
pereval_api_final/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── init_db.py
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
├── render.yaml
├── README.md
└── requirements.txt
```

## Local launch

### 1. Create and activate a virtual environment

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

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start PostgreSQL locally

```bash
docker compose up -d
```

Docker Compose creates PostgreSQL and applies the schema from:

```text
db/schema.sql
```

### 4. Create `.env`

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux / macOS:

```bash
cp .env.example .env
```

Local `.env` example:

```env
FSTR_DB_HOST=127.0.0.1
FSTR_DB_PORT=5433
FSTR_DB_NAME=pereval_db
FSTR_DB_LOGIN=pereval_user
FSTR_DB_PASS=pereval_pass
```

The project also supports `FSTR_LOGIN` and `FSTR_PASS`, because these names are mentioned in some versions of the task criteria.

For Render deployment, the project can use:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
INIT_DB_ON_START=1
```

### 5. Start the API locally

```bash
uvicorn app.main:app --reload
```

Local Swagger:

```text
http://127.0.0.1:8000/docs
```

## Database structure

The project uses a redesigned PostgreSQL schema:

- `users` - user personal and contact data;
- `coords` - pereval coordinates and height;
- `levels` - difficulty levels by season;
- `perevals` - main pereval records;
- `images` - pereval photos.

The `perevals` table contains the moderation field:

```text
status
```

Allowed status values:

```text
new
pending
accepted
rejected
```

A new record created through `POST /submitData` automatically receives:

```text
new
```

## API examples

### POST /submitData

Local request:

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

Hosted request:

```bash
curl -X POST https://pereval-api-final.onrender.com/submitData \
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

Successful response:

```json
{
  "status": 200,
  "message": "Отправлено успешно",
  "id": 1
}
```

Validation error:

```json
{
  "status": 400,
  "message": "Bad Request: не хватает или неверно заполнены поля"
}
```

Server error:

```json
{
  "status": 500,
  "message": "Описание ошибки"
}
```

### GET /submitData/{id}

```bash
curl https://pereval-api-final.onrender.com/submitData/1
```

The response includes full pereval data, user data, coordinates, difficulty levels, images and moderation status.

### PATCH /submitData/{id}

The method accepts the same JSON structure as `POST /submitData`.

It updates only records with status:

```text
new
```

User data is not edited:

- `fam`;
- `name`;
- `otc`;
- `email`;
- `phone`.

Successful response:

```json
{
  "state": 1,
  "message": "Запись успешно обновлена"
}
```

If the status is not `new`:

```json
{
  "state": 0,
  "message": "Редактирование запрещено: статус записи не new"
}
```

### GET /submitData/?user__email=<email>

```bash
curl "https://pereval-api-final.onrender.com/submitData/?user__email=tourist@example.com"
```

Returns a list of all perevals submitted by the given user email.

## Tests

Run tests:

```bash
pytest
```

The project contains:

- REST API tests through `TestClient`;
- environment variable config test;
- PostgreSQL integration test for `DatabaseManager`.

The DB integration test is skipped by default, so a normal `pytest` run does not require a local PostgreSQL database.

To run the DB integration test:

Windows PowerShell:

```powershell
$env:FSTR_TEST_DB="1"
pytest tests/test_database.py
```

Linux / macOS:

```bash
export FSTR_TEST_DB=1
pytest tests/test_database.py
```

## Git workflow

The project was developed in a separate feature branch and merged into the main working branch.

Example workflow:

```bash
git checkout -b feature/pereval-api
git add .
git commit -m "Add project configuration"
git commit -m "Add PostgreSQL database schema"
git commit -m "Implement Pereval REST API"
git commit -m "Add tests and API documentation"
git checkout master
git merge feature/pereval-api
```

## Criteria coverage

| Criterion | Status |
|---|---|
| Database access class | Completed |
| Sprint 1 REST API: POST /submitData | Completed |
| Sprint 2 REST API: GET, PATCH, GET by email | Completed |
| README.md documentation | Completed |
| Code style | Completed |
| Environment variables | Completed |
| Redesigned database structure | Completed |
| Swagger / OpenAPI documentation | Completed through FastAPI `/docs` |
| Tests | Completed |
| Hosting deployment | Completed on Render |
