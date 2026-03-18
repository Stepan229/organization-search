import uuid

from sqlalchemy import Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    address: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        back_populates="building",
        cascade="all, delete-orphan",
    )
