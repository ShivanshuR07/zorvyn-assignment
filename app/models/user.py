from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum as SQLAlchemyEnum, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin
from app.utils.enums import RoleEnum, UserStateEnum

if TYPE_CHECKING:
    from app.models.financial_record import FinancialRecord


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        SQLAlchemyEnum(RoleEnum, name="user_role", native_enum=False),
        nullable=False,
        default=RoleEnum.viewer,
    )
    state: Mapped[UserStateEnum] = mapped_column(
        SQLAlchemyEnum(UserStateEnum, name="user_state", native_enum=False),
        nullable=False,
        default=UserStateEnum.active,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_records: Mapped[list["FinancialRecord"]] = relationship(back_populates="created_by_user")
