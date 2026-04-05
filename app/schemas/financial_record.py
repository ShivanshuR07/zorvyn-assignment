from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.enums import RecordTypeEnum


class FinancialRecordCreate(BaseModel):
    amount: Decimal = Field(ge=0, decimal_places=2)
    type: RecordTypeEnum
    category: str = Field(min_length=1, max_length=100)
    record_date: date
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Category must not be empty.")
        return normalized

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        return normalized or None


class FinancialRecordUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    type: RecordTypeEnum | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    record_date: date | None = None
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Category must not be empty.")
        return normalized

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        return normalized or None


class FinancialRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: Decimal
    type: RecordTypeEnum
    category: str
    record_date: date
    notes: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class FinancialRecordListResponse(BaseModel):
    items: list[FinancialRecordRead]
    total: int
    limit: int
    offset: int
