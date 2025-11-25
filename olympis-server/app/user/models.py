import enum
import uuid
from typing import List

from sqlalchemy import String, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    external_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)

    profile: Mapped["UserProfile"] = relationship(cascade="save-update, delete")
    user_meta: Mapped["UserMetaData"] = relationship(cascade="save-update, delete")

    stores: Mapped[List["AssociationUserStore"]] = relationship(back_populates="user", cascade="delete")


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(String(320), unique=True)


class UserMetaData(Base, TimestampMixin):
    __tablename__ = "users_metadata"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    )


class StoreRole(str, enum.Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class AssociationUserStore(Base, TimestampMixin):
    __tablename__ = "association_user_store"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    )
    store_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("stores.id"),
        primary_key=True,
    )
    role: Mapped[StoreRole] = mapped_column(SAEnum(StoreRole, name="store_role"))

    user: Mapped["User"] = relationship(back_populates="stores")
    store: Mapped["Store"] = relationship(back_populates="users")
