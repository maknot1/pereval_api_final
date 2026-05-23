"""FastAPI application for the FSTR Pereval REST API."""

import os

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import DatabaseManager
from app.init_db import init_database
from app.schemas import (
    PerevalCreateSchema,
    SubmitResponseSchema,
    UpdateResponseSchema,
)

app = FastAPI(
    title="FSTR Pereval API",
    description="REST API для отправки данных о горных перевалах в ФСТР.",
    version="1.0.0",
)


@app.on_event("startup")
def initialize_database_on_startup() -> None:
    """Initialize database schema on hosted deployments when enabled."""

    if os.getenv("INIT_DB_ON_START") == "1":
        init_database()


def get_database() -> DatabaseManager:
    """FastAPI dependency for obtaining the database manager."""

    return DatabaseManager()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return 400 for invalid input according to the project requirements."""

    return JSONResponse(
        status_code=400,
        content={"status": 400, "message": "Bad Request: не хватает или неверно заполнены поля"},
    )


@app.post("/submitData", response_model=SubmitResponseSchema)
def submit_data(
    payload: PerevalCreateSchema,
    database: DatabaseManager = Depends(get_database),
):
    """Create a new pereval record."""

    try:
        pereval_id = database.add_pereval(payload.model_dump())
        return {"status": 200, "message": "Отправлено успешно", "id": pereval_id}
    except KeyError as exc:
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": f"Bad Request: отсутствует поле {exc}"},
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": str(exc)},
        )


@app.get("/submitData/{pereval_id}")
def get_submit_data(
    pereval_id: int,
    database: DatabaseManager = Depends(get_database),
):
    """Return full information about one pereval by id."""

    try:
        result = database.get_pereval_by_id(pereval_id)
        if result is None:
            return JSONResponse(
                status_code=404,
                content={"status": 404, "message": "Запись не найдена"},
            )
        return result
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": str(exc)},
        )


@app.patch("/submitData/{pereval_id}", response_model=UpdateResponseSchema)
def update_submit_data(
    pereval_id: int,
    payload: PerevalCreateSchema,
    database: DatabaseManager = Depends(get_database),
):
    """Update a pereval if it has status new."""

    return database.update_pereval(pereval_id, payload.model_dump())


@app.get("/submitData/")
def get_submit_data_by_email(
    user__email: str,
    database: DatabaseManager = Depends(get_database),
):
    """Return all pereval records submitted by user email."""

    try:
        return database.get_perevals_by_email(user__email)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": str(exc)},
        )
