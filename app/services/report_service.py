from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.errors import bad_request
from app.models.financial_record import FinancialRecord
from app.schemas.report import (
    CategoryBreakdownItem,
    CategoryBreakdownResponse,
    RecentActivityResponse,
    SummaryReport,
    TrendPoint,
    TrendResponse,
)
from app.utils.enums import RecordTypeEnum, TrendPeriodEnum, TrendTypeFilterEnum


ZERO = Decimal("0.00")


def _date_filtered_query(db: Session, *, date_from: date | None, date_to: date | None):
    if date_from and date_to and date_from > date_to:
        raise bad_request("date_from must be earlier than or equal to date_to.")
    query = db.query(FinancialRecord)
    if date_from:
        query = query.filter(FinancialRecord.record_date >= date_from)
    if date_to:
        query = query.filter(FinancialRecord.record_date <= date_to)
    return query


def get_summary(db: Session, *, date_from: date | None = None, date_to: date | None = None) -> SummaryReport:
    query = _date_filtered_query(db, date_from=date_from, date_to=date_to)
    total_income, total_expense = query.with_entities(
        func.coalesce(
            func.sum(case((FinancialRecord.type == RecordTypeEnum.income, FinancialRecord.amount), else_=0)),
            0,
        ),
        func.coalesce(
            func.sum(case((FinancialRecord.type == RecordTypeEnum.expense, FinancialRecord.amount), else_=0)),
            0,
        ),
    ).one()
    income = Decimal(total_income or 0).quantize(Decimal("0.01"))
    expense = Decimal(total_expense or 0).quantize(Decimal("0.01"))
    return SummaryReport(
        total_income=income,
        total_expense=expense,
        net_balance=(income - expense).quantize(Decimal("0.01")),
    )


def get_category_breakdown(
    db: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
) -> CategoryBreakdownResponse:
    query = _date_filtered_query(db, date_from=date_from, date_to=date_to)
    rows = (
        query.with_entities(
            FinancialRecord.category,
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .group_by(FinancialRecord.category, FinancialRecord.type)
        .order_by(func.sum(FinancialRecord.amount).desc(), FinancialRecord.category.asc())
        .all()
    )
    return CategoryBreakdownResponse(
        items=[
            CategoryBreakdownItem(
                category=category,
                type=record_type,
                total=Decimal(total).quantize(Decimal("0.01")),
            )
            for category, record_type, total in rows
        ]
    )


def get_trends(
    db: Session,
    *,
    period: TrendPeriodEnum,
    type_filter: TrendTypeFilterEnum,
    date_from: date | None = None,
    date_to: date | None = None,
) -> TrendResponse:
    trunc_unit = "week" if period == TrendPeriodEnum.weekly else "month"
    period_column = func.date_trunc(trunc_unit, FinancialRecord.record_date).label("period_start")
    query = _date_filtered_query(db, date_from=date_from, date_to=date_to)
    if type_filter != TrendTypeFilterEnum.all:
        query = query.filter(FinancialRecord.type == RecordTypeEnum(type_filter.value))
    rows = (
        query.with_entities(
            period_column,
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordTypeEnum.income, FinancialRecord.amount), else_=0)),
                0,
            ).label("total_income"),
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordTypeEnum.expense, FinancialRecord.amount), else_=0)),
                0,
            ).label("total_expense"),
        )
        .group_by(period_column)
        .order_by(period_column.asc())
        .all()
    )
    return TrendResponse(
        items=[
            TrendPoint(
                period=period,
                period_start=period_start.date() if hasattr(period_start, "date") else period_start,
                total_income=Decimal(total_income).quantize(Decimal("0.01")),
                total_expense=Decimal(total_expense).quantize(Decimal("0.01")),
                net_balance=(Decimal(total_income) - Decimal(total_expense)).quantize(Decimal("0.01")),
            )
            for period_start, total_income, total_expense in rows
        ]
    )


def get_recent_activity(
    db: Session,
    *,
    limit: int = 10,
    date_from: date | None = None,
    date_to: date | None = None,
) -> RecentActivityResponse:
    query = _date_filtered_query(db, date_from=date_from, date_to=date_to)
    items = (
        query.order_by(FinancialRecord.record_date.desc(), FinancialRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return RecentActivityResponse(items=items)
