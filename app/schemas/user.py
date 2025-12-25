from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Timestamped


class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, max_length=255)


class UserRead(Timestamped):
    email: EmailStr
    name: str | None
