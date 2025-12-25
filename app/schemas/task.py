from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import Timestamped


def _normalize_status(v: str) -> str:
    v_norm = v.strip().upper()
    allowed = {"PENDING", "IN_PROGRESS", "DONE", "CANCELLED"}
    if v_norm not in allowed:
        raise ValueError(f"Invalid status: {v!r}")
    return v_norm


class TaskCreate(BaseModel):
    user_id: UUID
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    priority: int | None = Field(default=None, ge=0, le=10)
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    priority: int | None = Field(default=None, ge=0, le=10)
    due_at: datetime | None = None
    status: str | None = None

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return _normalize_status(v)


class TaskStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        return _normalize_status(v)


class TaskRead(Timestamped):
    user_id: UUID
    title: str
    description: str | None
    status: str
    priority: int | None
    due_at: datetime | None
    completed_at: datetime | None
