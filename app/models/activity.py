import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)

    parent: Mapped["Activity | None"] = relationship(
        "Activity",
        remote_side="Activity.id",
        back_populates="children",
    )
    children: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        secondary="organization_activities",
        back_populates="activities",
    )

    __table_args__ = (CheckConstraint("level >= 1 AND level <= 3", name="activity_level_1_3"),)