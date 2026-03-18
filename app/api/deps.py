from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.services.building import BuildingService
from app.services.organization import OrganizationService
from app.services.search import SearchService


def get_organization_service(session: Session = Depends(get_session)) -> OrganizationService:
    return OrganizationService(session)


def get_building_service(session: Session = Depends(get_session)) -> BuildingService:
    return BuildingService(session)


def get_search_service(session: Session = Depends(get_session)) -> SearchService:
    return SearchService(session)
