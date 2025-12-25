from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class TaskStatus(StrEnum):
    pending = "PENDING"
    in_progress = "IN_PROGRESS"
    done = "DONE"
    cancelled = "CANCELLED"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    priority: int | None = Field(default=None, ge=0, le=10)
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    priority: int | None = Field(default=None, ge=0, le=10)
    due_at: datetime | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskRead(Timestamped):
    user_id: UUID
    title: str
    description: str | None
    status: str
    priority: int | None
    due_at: datetime | None
    completed_at: datetime | None
