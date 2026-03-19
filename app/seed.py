"""
Load test data: buildings, activities (tree up to 3 levels), organizations with phones.
Run after: alembic upgrade head
"""
import logging
import uuid

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Activity, Building, Organization, OrganizationActivity, OrganizationPhone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed(session: Session) -> None:
    # Make seeding idempotent: only reset data with fixed UUIDs used in this script.
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

    # Delete in FK-safe order.
    session.execute(
        delete(OrganizationActivity).where(OrganizationActivity.organization_id.in_(organization_ids)),
    )
    session.execute(
        delete(OrganizationPhone).where(OrganizationPhone.organization_id.in_(organization_ids)),
    )
    session.execute(delete(Organization).where(Organization.id.in_(organization_ids)))
    session.execute(delete(Activity).where(Activity.id.in_(activity_ids)))
    session.execute(delete(Building).where(Building.id.in_(building_ids)))
    session.flush()

    # Buildings
    b1 = Building(
        id=uuid.UUID("10000000-0000-0000-0000-000000000001"),
        address="г. Москва, ул. Ленина 1, офис 3",
        latitude=55.7558,
        longitude=37.6173,
    )
    b2 = Building(
        id=uuid.UUID("10000000-0000-0000-0000-000000000002"),
        address="г. Москва, ул. Блюхера, 32/1",
        latitude=55.7612,
        longitude=37.6205,
    )
    b3 = Building(
        id=uuid.UUID("10000000-0000-0000-0000-000000000003"),
        address="г. Москва, ул. Тверская, 10",
        latitude=55.7640,
        longitude=37.6050,
    )
    session.add_all([b1, b2, b3])
    session.flush()

    # Activities (tree, max level 3)
    # Level 1
    food = Activity(
        id=uuid.UUID("20000000-0000-0000-0000-000000000001"),
        name="Еда",
        parent_id=None,
        level=1,
    )
    cars = Activity(
        id=uuid.UUID("20000000-0000-0000-0000-000000000002"),
        name="Автомобили",
        parent_id=None,
        level=1,
    )
    session.add_all([food, cars])
    session.flush()

    # Level 2
    meat = Activity(
        id=uuid.UUID("20000000-0000-0000-0000-000000000011"),
        name="Мясная продукция",
        parent_id=food.id,
        level=2,
    )
    milk = Activity(
        id=uuid.UUID("20000000-0000-0000-0000-000000000012"),
        name="Молочная продукция",
        parent_id=food.id,
        level=2,
    )
    trucks = Activity(
        id=uuid.UUID("20000000-0000-0000-0000-000000000021"),
        name="Грузовые",
        parent_id=cars.id,
        level=2,
    )
    passenger = Activity(
        id=uuid.UUID("20000000-0000-0000-0000-000000000022"),
        name="Легковые",
        parent_id=cars.id,
        level=2,
    )
    session.add_all([meat, milk, trucks, passenger])
    session.flush()

    # Level 3
    parts = Activity(
        id=uuid.UUID("20000000-0000-0000-0000-000000000031"),
        name="Запчасти",
        parent_id=passenger.id,
        level=3,
    )
    accessories = Activity(
        id=uuid.UUID("20000000-0000-0000-0000-000000000032"),
        name="Аксессуары",
        parent_id=passenger.id,
        level=3,
    )
    session.add_all([parts, accessories])
    session.flush()

    # Organizations
    o1 = Organization(
        id=uuid.UUID("30000000-0000-0000-0000-000000000001"),
        name='ООО "Рога и Копыта"',
        building_id=b2.id,
    )
    session.add(o1)
    session.flush()
    session.add(OrganizationPhone(organization_id=o1.id, phone="2-222-222"))
    session.add(OrganizationPhone(organization_id=o1.id, phone="3-333-333"))
    session.add(OrganizationPhone(organization_id=o1.id, phone="8-923-666-13-13"))
    session.add(OrganizationActivity(organization_id=o1.id, activity_id=meat.id))
    session.add(OrganizationActivity(organization_id=o1.id, activity_id=milk.id))

    o2 = Organization(
        id=uuid.UUID("30000000-0000-0000-0000-000000000002"),
        name='ООО "Мясной двор"',
        building_id=b1.id,
    )
    session.add(o2)
    session.flush()
    session.add(OrganizationPhone(organization_id=o2.id, phone="8-800-555-00-01"))
    session.add(OrganizationActivity(organization_id=o2.id, activity_id=meat.id))

    o3 = Organization(
        id=uuid.UUID("30000000-0000-0000-0000-000000000003"),
        name='ИП "Автозапчасти"',
        building_id=b3.id,
    )
    session.add(o3)
    session.flush()
    session.add(OrganizationPhone(organization_id=o3.id, phone="8-495-123-45-67"))
    session.add(OrganizationActivity(organization_id=o3.id, activity_id=parts.id))
    session.add(OrganizationActivity(organization_id=o3.id, activity_id=accessories.id))

    o4 = Organization(
        id=uuid.UUID("30000000-0000-0000-0000-000000000004"),
        name='ООО "Молоко и мёд"',
        building_id=b2.id,
    )
    session.add(o4)
    session.flush()
    session.add(OrganizationPhone(organization_id=o4.id, phone="8-800-100-20-30"))
    session.add(OrganizationActivity(organization_id=o4.id, activity_id=milk.id))
    session.add(OrganizationActivity(organization_id=o4.id, activity_id=food.id))

    session.commit()
    logger.info("Seed data loaded.")


def main() -> None:
    session = SessionLocal()
    try:
        seed(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
