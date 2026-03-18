import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.repositories.activity import ActivityRepository
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


class SearchService:
    def __init__(self, session: Session) -> None:
        self._activity_repo = ActivityRepository(session)
        self._building_repo = BuildingRepository(session)
        self._org_repo = OrganizationRepository(session)

    def organizations_by_activity(
        self,
        activity_id: uuid.UUID,
        include_subtree: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OrganizationRead]:
        if self._activity_repo.get_by_id(activity_id) is None:
            raise NotFoundError("Activity not found")
        if include_subtree:
            activity_ids = self._activity_repo.get_descendant_ids(activity_id)
        else:
            activity_ids = [activity_id]
        orgs = self._org_repo.get_by_activity_ids(activity_ids, limit=limit, offset=offset)
        return [_org_to_read(o) for o in orgs]

    def organizations_by_activity_name(
        self,
        activity_name: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OrganizationRead]:
        activity = self._activity_repo.get_by_name(activity_name)
        if not activity:
            raise NotFoundError("Activity not found")
        activity_ids = self._activity_repo.get_descendant_ids(activity.id)
        orgs = self._org_repo.get_by_activity_ids(activity_ids, limit=limit, offset=offset)
        return [_org_to_read(o) for o in orgs]

    def organizations_in_radius(
        self,
        lat: float,
        lon: float,
        radius_m: float,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OrganizationRead]:
        if radius_m <= 0:
            raise BadRequestError("radius_m must be positive")
        building_ids = self._building_repo.get_ids_in_radius(lat, lon, radius_m)
        orgs = self._org_repo.get_by_building_ids(building_ids, limit=limit, offset=offset)
        return [_org_to_read(o) for o in orgs]

    def organizations_in_bbox(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OrganizationRead]:
        if lat_min > lat_max or lon_min > lon_max:
            raise BadRequestError("Invalid bbox: lat_min <= lat_max and lon_min <= lon_max")
        building_ids = self._building_repo.get_ids_in_bbox(lat_min, lat_max, lon_min, lon_max)
        orgs = self._org_repo.get_by_building_ids(building_ids, limit=limit, offset=offset)
        return [_org_to_read(o) for o in orgs]

    def organizations_by_name(
        self,
        q: str,
        match_type: str = "contains",
        limit: int = 100,
        offset: int = 0,
    ) -> list[OrganizationRead]:
        if not q or not q.strip():
            raise BadRequestError("Search query cannot be empty")
        if match_type not in ("contains", "prefix", "exact"):
            raise BadRequestError("match_type must be one of: contains, prefix, exact")
        orgs = self._org_repo.search_by_name(q, match_type=match_type, limit=limit, offset=offset)
        return [_org_to_read(o) for o in orgs]
