import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.building import BuildingRepository
from app.repositories.organization import OrganizationRepository
from app.schemas import ActivityShort, BuildingRead, OrganizationRead


def _org_to_read(org) -> OrganizationRead:
    return OrganizationRead(
        id=org.id,
        name=org.name,
        building_id=org.building_id,
        building=BuildingRead.model_validate(org.building) if org.building else None,
        activities=[ActivityShort.model_validate(a) for a in org.activities],
        phones=[p.phone for p in org.phones],
    )


class BuildingService:
    def __init__(self, session: Session) -> None:
        self._building_repo = BuildingRepository(session)
        self._org_repo = OrganizationRepository(session)

    def get_by_id(self, building_id: uuid.UUID) -> BuildingRead:
        b = self._building_repo.get_by_id(building_id)
        if not b:
            raise NotFoundError("Building not found")
        return BuildingRead.model_validate(b)

    def list_buildings(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BuildingRead]:
        buildings = self._building_repo.get_all(limit=limit, offset=offset)
        return [BuildingRead.model_validate(b) for b in buildings]

    def list_organizations_in_building(
        self,
        building_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OrganizationRead]:
        if self._building_repo.get_by_id(building_id) is None:
            raise NotFoundError("Building not found")
        orgs = self._org_repo.get_by_building(building_id, limit=limit, offset=offset)
        return [_org_to_read(o) for o in orgs]
