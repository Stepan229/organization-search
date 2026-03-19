import os
import uuid

import pytest
from starlette.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

from app.core.config import Settings
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models import Activity, Building, Organization, OrganizationActivity, OrganizationPhone

load_dotenv()

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
TEST_API_KEY = os.environ.get("TEST_API_KEY", "test-api-key")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL must be set for tests (PostgreSQL). "
        "Set it in .env or export it before running pytest."
    )
if not TEST_DATABASE_URL.startswith("postgresql"):
    raise RuntimeError(f"Only PostgreSQL is supported for tests, got: {TEST_DATABASE_URL!r}")


@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        database_url=TEST_DATABASE_URL,
        api_key=TEST_API_KEY,
    )


@pytest.fixture(scope="session")
def engine(test_settings):
    url = test_settings.database_url
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def engine_fresh(test_settings):
    """Per-test engine so each test runs in a fresh connection context."""
    url = test_settings.database_url
    eng = create_engine(url)
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture(scope="session")
def SessionLocalTest(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def SessionLocalFresh(engine_fresh):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine_fresh)


@pytest.fixture
def db_session(engine_fresh, SessionLocalFresh):
    """Use fresh engine per test for isolation (avoids UNIQUE conflicts across tests)."""
    connection = engine_fresh.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)
    try:
        yield session
    finally:
        # The test itself may call commit/rollback; rollbacking the original
        # `transaction` object can emit SAWarning if it is already deassociated.
        # `session.rollback()` is safe and uses the current state.
        try:
            session.rollback()
        except Exception:
            pass
        session.close()
        connection.close()


@pytest.fixture
def client(test_settings, db_session):
    from app.core.config import get_settings

    app = create_app()
    app.dependency_overrides[get_settings] = lambda: test_settings
    # Override so the app gets our test session (return value, not generator)
    app.dependency_overrides[get_session] = lambda: db_session

    with TestClient(app) as c:
        yield c


@pytest.fixture
def seed_data(db_session):
    """Insert test data (flush only so rollback clears it). Use explicit UUIDs for reproducibility."""
    building_ids = [
        uuid.UUID("10000000-0000-0000-0000-000000000001"),
        uuid.UUID("10000000-0000-0000-0000-000000000002"),
    ]
    activity_ids = [
        uuid.UUID("20000000-0000-0000-0000-000000000001"),
        uuid.UUID("20000000-0000-0000-0000-000000000011"),
        uuid.UUID("20000000-0000-0000-0000-000000000012"),
    ]
    organization_ids = [
        uuid.UUID("30000000-0000-0000-0000-000000000001"),
        uuid.UUID("30000000-0000-0000-0000-000000000002"),
    ]

    # Ensure deterministic fixture behavior regardless of previous tests.
    db_session.execute(
        delete(OrganizationActivity).where(OrganizationActivity.organization_id.in_(organization_ids)),
    )
    db_session.execute(
        delete(OrganizationPhone).where(OrganizationPhone.organization_id.in_(organization_ids)),
    )
    db_session.execute(delete(Organization).where(Organization.id.in_(organization_ids)))
    db_session.execute(delete(Activity).where(Activity.id.in_(activity_ids)))
    db_session.execute(delete(Building).where(Building.id.in_(building_ids)))

    id_b1 = uuid.UUID("10000000-0000-0000-0000-000000000001")
    id_b2 = uuid.UUID("10000000-0000-0000-0000-000000000002")
    b1 = Building(
        id=id_b1,
        address="г. Москва, ул. Ленина 1",
        latitude=55.7558,
        longitude=37.6173,
    )
    b2 = Building(
        id=id_b2,
        address="г. Москва, ул. Блюхера, 32/1",
        latitude=55.7612,
        longitude=37.6205,
    )
    db_session.add(b1)
    db_session.flush()
    db_session.add(b2)
    db_session.flush()

    id_food = uuid.UUID("20000000-0000-0000-0000-000000000001")
    id_meat = uuid.UUID("20000000-0000-0000-0000-000000000011")
    id_milk = uuid.UUID("20000000-0000-0000-0000-000000000012")
    food = Activity(id=id_food, name="Еда", parent_id=None, level=1)
    meat = Activity(id=id_meat, name="Мясная продукция", parent_id=id_food, level=2)
    milk = Activity(id=id_milk, name="Молочная продукция", parent_id=id_food, level=2)
    db_session.add(food)
    db_session.flush()
    db_session.add(meat)
    db_session.add(milk)
    db_session.flush()

    id_o1 = uuid.UUID("30000000-0000-0000-0000-000000000001")
    id_o2 = uuid.UUID("30000000-0000-0000-0000-000000000002")
    o1 = Organization(id=id_o1, name='ООО "Рога и Копыта"', building_id=id_b2)
    o2 = Organization(id=id_o2, name='ООО "Мясной двор"', building_id=id_b1)
    db_session.add(o1)
    db_session.flush()
    db_session.add(OrganizationPhone(organization_id=id_o1, phone="2-222-222"))
    db_session.add(OrganizationActivity(organization_id=id_o1, activity_id=id_meat))
    db_session.add(OrganizationActivity(organization_id=id_o1, activity_id=id_milk))
    db_session.add(o2)
    db_session.flush()
    db_session.add(OrganizationActivity(organization_id=id_o2, activity_id=id_meat))
    db_session.flush()

    return {"building_id": id_b2, "activity_id": id_food, "org_id": id_o1}


API_KEY_HEADERS = {"X-API-Key": TEST_API_KEY}
