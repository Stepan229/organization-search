import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.organization import OrganizationRepository
from app.schemas import ActivityShort, BuildingShort, OrganizationDetail


class OrganizationService:
    def __init__(self, session: Session) -> None:
        self._repo = OrganizationRepository(session)

    def get_by_id(self, organization_id: uuid.UUID) -> OrganizationDetail:
        org = self._repo.get_by_id(organization_id)
        if not org:
            raise NotFoundError("Organization not found")
        return _org_to_detail(org)


def _org_to_detail(org) -> OrganizationDetail:
    return OrganizationDetail(
        id=org.id,
        name=org.name,
        building_id=org.building_id,
        building=BuildingShort.model_validate(org.building),
        activities=[ActivityShort.model_validate(a) for a in org.activities],
        phones=[p.phone for p in org.phones],
    )
