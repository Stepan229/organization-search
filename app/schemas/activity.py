from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivityShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    level: int


class ActivityRead(ActivityShort):
    parent_id: UUID | None = None
