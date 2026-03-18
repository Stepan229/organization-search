from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_organization_service
from app.core.security import require_api_key
from app.schemas import OrganizationDetail
from app.services.organization import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get(
    "/{organization_id}",
    response_model=OrganizationDetail,
    summary="Получить организацию по идентификатору",
    description="Возвращает полную информацию об организации, включая здание, виды деятельности и телефоны.",
)
def get_organization(
    organization_id: UUID,
    _: None = Depends(require_api_key),
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationDetail:
    return service.get_by_id(organization_id)
