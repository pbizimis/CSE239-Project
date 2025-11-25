from typing import Any
import uuid
import enum

from sqlalchemy import ForeignKey, String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.jobs.models import Job
from app.models import Base, TimestampMixin
from app.stores.models import Store


class CampaignState(str, enum.Enum):
    setup = "setup"
    active = "active"
    archived = "archived"


class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(2048))
    status: Mapped[CampaignState] = mapped_column(
        SAEnum(
            CampaignState,
            name="campaign_state",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=CampaignState.setup,
    )

    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("jobs.id"))
    job: Mapped[Job | None] = relationship(cascade="delete")

    store_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("stores.id")
    )
    store: Mapped["Store"] = relationship(back_populates="campaigns")

    campaign_meta: Mapped["CampaignMetaData"] = relationship(cascade="save-update, delete")


class CampaignMetaData(Base, TimestampMixin):
    __tablename__ = "campaigns_metadata"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("campaigns.id"), primary_key=True
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONB)
