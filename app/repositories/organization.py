import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Organization


class OrganizationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        return self._session.get(
            Organization,
            organization_id,
            options=[
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities),
            ],
        )

    def get_by_building(
        self,
        building_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Organization]:
        q = (
            select(Organization)
            .where(Organization.building_id == building_id)
            .options(
                joinedload(Organization.building),
                joinedload(Organization.activities),
                joinedload(Organization.phones),
            )
            .order_by(Organization.name)
            .limit(limit)
            .offset(offset)
        )
        return list(self._session.scalars(q).unique().all())

    def get_by_activity_ids(
        self,
        activity_ids: list[uuid.UUID],
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Organization]:
        if not activity_ids:
            return []
        from app.models import OrganizationActivity
        q = (
            select(Organization)
            .join(OrganizationActivity, Organization.id == OrganizationActivity.organization_id)
            .where(OrganizationActivity.activity_id.in_(activity_ids))
            .options(
                joinedload(Organization.building),
                joinedload(Organization.activities),
                joinedload(Organization.phones),
            )
            .distinct()
            .order_by(Organization.name)
            .limit(limit)
            .offset(offset)
        )
        return list(self._session.scalars(q).unique().all())

    def get_by_building_ids(
        self,
        building_ids: list[uuid.UUID],
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Organization]:
        if not building_ids:
            return []
        q = (
            select(Organization)
            .where(Organization.building_id.in_(building_ids))
            .options(
                joinedload(Organization.building),
                joinedload(Organization.activities),
                joinedload(Organization.phones),
            )
            .order_by(Organization.name)
            .limit(limit)
            .offset(offset)
        )
        return list(self._session.scalars(q).unique().all())

    def search_by_name(
        self,
        query: str,
        *,
        match_type: str = "contains",
        limit: int = 100,
        offset: int = 0,
    ) -> list[Organization]:
        if not query or not query.strip():
            return []
        q = (
            select(Organization)
            .options(
                joinedload(Organization.building),
                joinedload(Organization.activities),
                joinedload(Organization.phones),
            )
            .order_by(Organization.name)
            .limit(limit)
            .offset(offset)
        )
        if match_type == "exact":
            q = q.where(Organization.name == query.strip())
        elif match_type == "prefix":
            q = q.where(Organization.name.ilike(f"{query.strip()}%"))
        else:
            q = q.where(Organization.name.ilike(f"%{query.strip()}%"))
        return list(self._session.scalars(q).unique().all())
