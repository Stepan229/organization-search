"""Add UNIQUE constraint for activity name.

Revision id: 002
Revises: 001
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Ensure deterministic lookup of activity subtree by name.
    op.create_unique_constraint("uq_activities_name", "activities", ["name"])


def downgrade() -> None:
    op.drop_constraint("uq_activities_name", "activities", type_="unique")

