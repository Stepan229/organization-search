from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.activity import ActivityShort
from app.schemas.building import BuildingShort


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    building_id: UUID
    building: BuildingShort | None = None
    activities: list[ActivityShort] = []
    phones: list[str] = []


class OrganizationDetail(OrganizationRead):
    building: BuildingShort
    activities: list[ActivityShort]
    phones: list[str]
