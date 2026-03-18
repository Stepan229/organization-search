"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-03-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "buildings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("address", sa.String(512), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_buildings_address"), "buildings", ["address"], unique=False)
    op.create_index(
        "ix_buildings_lat_lon",
        "buildings",
        ["latitude", "longitude"],
        unique=False,
    )

    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.CheckConstraint("level >= 1 AND level <= 3", name="activity_level_1_3"),
        sa.ForeignKeyConstraint(["parent_id"], ["activities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activities_name"), "activities", ["name"], unique=False)
    op.create_index(
        op.f("ix_activities_parent_id"),
        "activities",
        ["parent_id"],
        unique=False,
    )

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["building_id"],
            ["buildings.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_organizations_building_id"),
        "organizations",
        ["building_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organizations_name"),
        "organizations",
        ["name"],
        unique=False,
    )

    op.create_table(
        "organization_phones",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone", sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_organization_phones_organization_id"),
        "organization_phones",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "organization_activities",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activities.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("organization_id", "activity_id"),
    )


def downgrade() -> None:
    op.drop_table("organization_activities")
    op.drop_index(
        op.f("ix_organization_phones_organization_id"),
        table_name="organization_phones",
    )
    op.drop_table("organization_phones")
    op.drop_index(op.f("ix_organizations_name"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_building_id"), table_name="organizations")
    op.drop_table("organizations")
    op.drop_index(op.f("ix_activities_parent_id"), table_name="activities")
    op.drop_index(op.f("ix_activities_name"), table_name="activities")
    op.drop_table("activities")
    op.drop_index("ix_buildings_lat_lon", table_name="buildings")
    op.drop_index(op.f("ix_buildings_address"), table_name="buildings")
    op.drop_table("buildings")
