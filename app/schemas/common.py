from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Timestamped(ORMBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
