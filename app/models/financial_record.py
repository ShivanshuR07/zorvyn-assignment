from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, Enum as SQLAlchemyEnum, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin
from app.utils.enums import RecordTypeEnum

if TYPE_CHECKING:
    from app.models.user import User


class FinancialRecord(TimestampMixin, Base):
    __tablename__ = "financial_records"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="amount_non_negative"),
        Index("ix_financial_records_type", "type"),
        Index("ix_financial_records_category", "category"),
        Index("ix_financial_records_record_date", "record_date"),
        Index("ix_financial_records_created_by", "created_by"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    type: Mapped[RecordTypeEnum] = mapped_column(
        SQLAlchemyEnum(RecordTypeEnum, name="record_type", native_enum=False),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    created_by_user: Mapped["User"] = relationship(back_populates="created_records")
