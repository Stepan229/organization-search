from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_search_service
from app.core.security import require_api_key
from app.schemas import OrganizationRead
from app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get(
    "/organizations/by-name",
    response_model=list[OrganizationRead],
    summary="Поиск организаций по названию",
    description="Поиск организаций по названию с выбором типа совпадения: содержит, префикс или точное совпадение.",
)
def search_organizations_by_name(
    _: None = Depends(require_api_key),
    service: SearchService = Depends(get_search_service),
    q: str = Query(..., min_length=1, description="Строка поиска по названию организации"),
    match_type: str = Query("contains", description="Тип совпадения: contains (содержит), prefix (начинается с), exact (точное)"),
    limit: int = Query(100, ge=1, le=500, description="Максимальное количество записей в ответе"),
    offset: int = Query(0, ge=0, description="Смещение для постраничной выборки"),
) -> list[OrganizationRead]:
    return service.organizations_by_name(q, match_type=match_type, limit=limit, offset=offset)


@router.get(
    "/organizations/by-activity",
    response_model=list[OrganizationRead],
    summary="Поиск организаций по виду деятельности (с учётом поддерева)",
    description="Поиск организаций по названию вида деятельности с учётом всех дочерних видов (например, «Еда» вернёт Еда, Мясная продукция, Молочная продукция).",
)
def search_organizations_by_activity_name(
    _: None = Depends(require_api_key),
    service: SearchService = Depends(get_search_service),
    activity_name: str = Query(..., description="Название вида деятельности (например, Еда)"),
    limit: int = Query(100, ge=1, le=500, description="Максимальное количество записей в ответе"),
    offset: int = Query(0, ge=0, description="Смещение для постраничной выборки"),
) -> list[OrganizationRead]:
    return service.organizations_by_activity_name(activity_name, limit=limit, offset=offset)


@router.get(
    "/organizations/geo/radius",
    response_model=list[OrganizationRead],
    summary="Организации в радиусе",
    description="Список организаций, находящихся в зданиях в заданном радиусе (в метрах) от указанной точки.",
)
def search_organizations_in_radius(
    _: None = Depends(require_api_key),
    service: SearchService = Depends(get_search_service),
    lat: float = Query(..., ge=-90, le=90, description="Широта точки (latitude)"),
    lon: float = Query(..., ge=-180, le=180, description="Долгота точки (longitude)"),
    radius_m: float = Query(..., gt=0, description="Радиус в метрах"),
    limit: int = Query(100, ge=1, le=500, description="Максимальное количество записей в ответе"),
    offset: int = Query(0, ge=0, description="Смещение для постраничной выборки"),
) -> list[OrganizationRead]:
    return service.organizations_in_radius(lat, lon, radius_m, limit=limit, offset=offset)


@router.get(
    "/organizations/geo/box",
    response_model=list[OrganizationRead],
    summary="Организации в прямоугольной области",
    description="Список организаций, находящихся в зданиях внутри прямоугольной области (лат/лон от min до max).",
)
def search_organizations_in_box(
    _: None = Depends(require_api_key),
    service: SearchService = Depends(get_search_service),
    lat_min: float = Query(..., ge=-90, le=90, description="Минимальная широта (lat_min)"),
    lat_max: float = Query(..., ge=-90, le=90, description="Максимальная широта (lat_max)"),
    lon_min: float = Query(..., ge=-180, le=180, description="Минимальная долгота (lon_min)"),
    lon_max: float = Query(..., ge=-180, le=180, description="Максимальная долгота (lon_max)"),
    limit: int = Query(100, ge=1, le=500, description="Максимальное количество записей в ответе"),
    offset: int = Query(0, ge=0, description="Смещение для постраничной выборки"),
) -> list[OrganizationRead]:
    return service.organizations_in_bbox(
        lat_min, lat_max, lon_min, lon_max,
        limit=limit, offset=offset,
    )
