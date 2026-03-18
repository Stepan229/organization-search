"""Test that activity level is limited to 1-3 (DB constraint)."""
import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Activity
from tests.conftest import API_KEY_HEADERS


def test_activity_level_constraint_max_3(db_session):
    """Inserting an activity with level 4 must violate the check constraint."""
    root = Activity(
        id=uuid.uuid4(),
        name="Root",
        parent_id=None,
        level=1,
    )
    db_session.add(root)
    db_session.flush()

    child = Activity(
        id=uuid.uuid4(),
        name="Child",
        parent_id=root.id,
        level=4,  # invalid: max is 3
    )
    db_session.add(child)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
