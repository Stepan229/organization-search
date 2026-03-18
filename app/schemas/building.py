from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BuildingShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    address: str
    latitude: float
    longitude: float


class BuildingRead(BuildingShort):
    pass
