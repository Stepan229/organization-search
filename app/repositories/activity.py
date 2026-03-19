import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Activity


class ActivityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, activity_id: uuid.UUID) -> Activity | None:
        return self._session.get(Activity, activity_id)

    def get_by_name(self, name: str) -> Activity | None:
        q = select(Activity).where(Activity.name == name).limit(1)
        return self._session.scalar(q)

    def get_descendant_ids(self, activity_id: uuid.UUID, max_level: int = 3) -> list[uuid.UUID]:
        # Рекурсивный CTE для обхода дерева
        cte = (
            select(Activity.id, Activity.level)
            .where(Activity.id == activity_id)
            .cte(name="tree", recursive=True)
        )
        child = select(Activity.id, Activity.level).where(
            Activity.parent_id == cte.c.id,
            Activity.level == cte.c.level + 1,
            Activity.level <= max_level,
        )
        cte = cte.union_all(child)
        q = select(cte.c.id).distinct()
        rows = self._session.execute(q).all()
        return [r[0] for r in rows]
