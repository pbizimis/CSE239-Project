import enum
import uuid
from typing import Any, List

from sqlalchemy import ForeignKey, String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.jobs.models import Job
from app.models import Base, TimestampMixin


class StoreState(str, enum.Enum):
    setup = "setup"
    active = "active"
    archived = "archived"


class Store(Base, TimestampMixin):
    __tablename__ = "stores"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(2048))
    status: Mapped[StoreState] = mapped_column(
        SAEnum(
            StoreState,
            name="store_state",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=StoreState.setup,
    )

    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("jobs.id"))
    job: Mapped[Job | None] = relationship(cascade="save-update, delete")

    users: Mapped[List["AssociationUserStore"]] = relationship(
        back_populates="store", cascade="delete"
    )

    campaigns: Mapped[List["Campaign"]] = relationship(
        back_populates="store", cascade="delete"
    )

    store_meta: Mapped["StoreMetaData"] = relationship(cascade="delete")


class StoreMetaData(Base, TimestampMixin):
    __tablename__ = "stores_metadata"

    store_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("stores.id"), primary_key=True
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONB)
