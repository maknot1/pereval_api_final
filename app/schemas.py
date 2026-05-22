"""Pydantic schemas for the FSTR Pereval REST API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserSchema(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    fam: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    otc: Optional[str] = Field(default="", max_length=100)
    phone: str = Field(..., min_length=3, max_length=50)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("email must contain a valid @ address")
        return value


class CoordsSchema(BaseModel):
    latitude: float
    longitude: float
    height: int = Field(..., ge=0)


class LevelSchema(BaseModel):
    winter: Optional[str] = ""
    summer: Optional[str] = ""
    autumn: Optional[str] = ""
    spring: Optional[str] = ""


class ImageSchema(BaseModel):
    data: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=255)


class PerevalCreateSchema(BaseModel):
    beauty_title: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    other_titles: Optional[str] = Field(default="", max_length=255)
    connect: Optional[str] = Field(default="")
    add_time: Optional[datetime] = None
    user: UserSchema
    coords: CoordsSchema
    level: LevelSchema
    images: list[ImageSchema] = Field(default_factory=list)


class SubmitResponseSchema(BaseModel):
    status: int
    message: str
    id: Optional[int] = None


class UpdateResponseSchema(BaseModel):
    state: int
    message: str


class PerevalReadSchema(PerevalCreateSchema):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)
