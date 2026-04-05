from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.schemas.report import (
    CategoryBreakdownResponse,
    RecentActivityResponse,
    SummaryReport,
    TrendResponse,
)
from app.services.report_service import get_category_breakdown, get_recent_activity, get_summary, get_trends
from app.utils.enums import RoleEnum, TrendPeriodEnum, TrendTypeFilterEnum


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=SummaryReport)
def summary_report(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _: object = Depends(require_roles(RoleEnum.analyst, RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> SummaryReport:
    return get_summary(db, date_from=date_from, date_to=date_to)


@router.get("/category-breakdown", response_model=CategoryBreakdownResponse)
def category_breakdown_report(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _: object = Depends(require_roles(RoleEnum.analyst, RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> CategoryBreakdownResponse:
    return get_category_breakdown(db, date_from=date_from, date_to=date_to)


@router.get("/trends", response_model=TrendResponse)
def trends_report(
    period: TrendPeriodEnum = Query(default=TrendPeriodEnum.monthly),
    type: TrendTypeFilterEnum = Query(default=TrendTypeFilterEnum.all),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _: object = Depends(require_roles(RoleEnum.analyst, RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> TrendResponse:
    return get_trends(
        db,
        period=period,
        type_filter=type,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/recent-activity", response_model=RecentActivityResponse)
def recent_activity_report(
    limit: int = Query(default=10, ge=1, le=50),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _: object = Depends(require_roles(RoleEnum.analyst, RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> RecentActivityResponse:
    return get_recent_activity(db, limit=limit, date_from=date_from, date_to=date_to)
