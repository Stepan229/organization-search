import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv

from app.db.base import Base
from app.models import Activity, Building, Organization, OrganizationActivity, OrganizationPhone
from app.seed import seed


load_dotenv()
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


def make_session() -> Session:
    if not TEST_DATABASE_URL or not TEST_DATABASE_URL.startswith("postgresql"):
        pytest.skip("Seed/unique tests require PostgreSQL via TEST_DATABASE_URL")

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def test_activity_name_unique_constraint():
    session = make_session()
    try:
        a1 = Activity(id=uuid.uuid4(), name="Еда", parent_id=None, level=1)
        a2 = Activity(id=uuid.uuid4(), name="Еда", parent_id=None, level=1)
        session.add_all([a1, a2])
        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()


def test_seed_idempotent_postgres():
    session = make_session()
    try:
        seed(session)
        seed(session)
        # Cleanup fixed seed data so other tests can insert the same UUIDs.
        building_ids = [
            uuid.UUID("10000000-0000-0000-0000-000000000001"),
            uuid.UUID("10000000-0000-0000-0000-000000000002"),
            uuid.UUID("10000000-0000-0000-0000-000000000003"),
        ]
        activity_ids = [
            uuid.UUID("20000000-0000-0000-0000-000000000001"),
            uuid.UUID("20000000-0000-0000-0000-000000000002"),
            uuid.UUID("20000000-0000-0000-0000-000000000011"),
            uuid.UUID("20000000-0000-0000-0000-000000000012"),
            uuid.UUID("20000000-0000-0000-0000-000000000021"),
            uuid.UUID("20000000-0000-0000-0000-000000000022"),
            uuid.UUID("20000000-0000-0000-0000-000000000031"),
            uuid.UUID("20000000-0000-0000-0000-000000000032"),
        ]
        organization_ids = [
            uuid.UUID("30000000-0000-0000-0000-000000000001"),
            uuid.UUID("30000000-0000-0000-0000-000000000002"),
            uuid.UUID("30000000-0000-0000-0000-000000000003"),
            uuid.UUID("30000000-0000-0000-0000-000000000004"),
        ]

        session.execute(
            delete(OrganizationActivity).where(OrganizationActivity.organization_id.in_(organization_ids)),
        )
        session.execute(
            delete(OrganizationPhone).where(OrganizationPhone.organization_id.in_(organization_ids)),
        )
        session.execute(delete(Organization).where(Organization.id.in_(organization_ids)))
        session.execute(delete(Activity).where(Activity.id.in_(activity_ids)))
        session.execute(delete(Building).where(Building.id.in_(building_ids)))
        session.commit()
    finally:
        session.rollback()
        session.close()

