from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.financial_record import FinancialRecordRead
from app.utils.enums import RecordTypeEnum, TrendPeriodEnum


class SummaryReport(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal


class CategoryBreakdownItem(BaseModel):
    category: str
    type: RecordTypeEnum
    total: Decimal


class CategoryBreakdownResponse(BaseModel):
    items: list[CategoryBreakdownItem]


class TrendPoint(BaseModel):
    period: TrendPeriodEnum
    period_start: date
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal


class TrendResponse(BaseModel):
    items: list[TrendPoint]


class RecentActivityResponse(BaseModel):
    items: list[FinancialRecordRead]
