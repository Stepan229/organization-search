from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_building_service
from app.core.security import require_api_key
from app.schemas import BuildingRead, OrganizationRead
from app.services.building import BuildingService

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get(
    "",
    response_model=list[BuildingRead],
    summary="Список зданий",
    description="Возвращает список зданий с пагинацией.",
)
def list_buildings(
    _: None = Depends(require_api_key),
    service: BuildingService = Depends(get_building_service),
    limit: int = Query(100, ge=1, le=500, description="Максимальное количество записей в ответе"),
    offset: int = Query(0, ge=0, description="Смещение для постраничной выборки"),
) -> list[BuildingRead]:
    return service.list_buildings(limit=limit, offset=offset)


@router.get(
    "/{building_id}",
    response_model=BuildingRead,
    summary="Получить здание по идентификатору",
)
def get_building(
    building_id: UUID,
    _: None = Depends(require_api_key),
    service: BuildingService = Depends(get_building_service),
) -> BuildingRead:
    return service.get_by_id(building_id)


@router.get(
    "/{building_id}/organizations",
    response_model=list[OrganizationRead],
    summary="Список организаций в здании",
    description="Возвращает все организации, находящиеся в указанном здании.",
)
def list_organizations_in_building(
    building_id: UUID,
    _: None = Depends(require_api_key),
    service: BuildingService = Depends(get_building_service),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[OrganizationRead]:
    return service.list_organizations_in_building(building_id, limit=limit, offset=offset)
