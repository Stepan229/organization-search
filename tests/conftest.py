import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models import Activity, Building, Organization, OrganizationActivity, OrganizationPhone

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "sqlite:///:memory:",
)


@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        database_url=TEST_DATABASE_URL,
        api_key="test-api-key",
    )


@pytest.fixture(scope="session")
def engine(test_settings):
    url = test_settings.database_url
    if url.startswith("sqlite"):
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(url)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def engine_fresh(test_settings):
    """Per-test engine for SQLite so each test gets a fresh in-memory DB."""
    url = test_settings.database_url
    if url.startswith("sqlite"):
        eng = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
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
    yield session
    session.close()
    transaction.rollback()
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


API_KEY_HEADERS = {"X-API-Key": "test-api-key"}
