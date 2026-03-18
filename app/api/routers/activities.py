from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_search_service
from app.core.security import require_api_key
from app.schemas import OrganizationRead
from app.services.search import SearchService

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get(
    "/{activity_id}/organizations",
    response_model=list[OrganizationRead],
    summary="Список организаций по виду деятельности",
    description="Возвращает организации, относящиеся к указанному виду деятельности. При include_subtree=true дополнительно учитываются организации из дочерних видов деятельности.",
)
def list_organizations_by_activity(
    activity_id: UUID,
    _: None = Depends(require_api_key),
    service: SearchService = Depends(get_search_service),
    include_subtree: bool = Query(False, description="Включать организации из дочерних видов деятельности"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[OrganizationRead]:
    return service.organizations_by_activity(
        activity_id,
        include_subtree=include_subtree,
        limit=limit,
        offset=offset,
    )
