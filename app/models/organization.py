import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    building_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("buildings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    building: Mapped["Building"] = relationship("Building", back_populates="organizations")
    phones: Mapped[list["OrganizationPhone"]] = relationship(
        "OrganizationPhone",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        secondary="organization_activities",
        back_populates="organizations",
    )


class OrganizationPhone(Base):
    __tablename__ = "organization_phones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phone: Mapped[str] = mapped_column(String(64), nullable=False)

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="phones",
    )


class OrganizationActivity(Base):
    __tablename__ = "organization_activities"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    )