from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.schemas.report import CategoryBreakdownResponse, SummaryReport, TrendResponse
from app.services.report_service import get_category_breakdown, get_summary, get_trends
from app.utils.enums import RoleEnum, TrendPeriodEnum, TrendTypeFilterEnum


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=SummaryReport)
def dashboard_summary(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _: object = Depends(require_roles(RoleEnum.viewer, RoleEnum.analyst, RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> SummaryReport:
    return get_summary(db, date_from=date_from, date_to=date_to)


@router.get("/category-breakdown", response_model=CategoryBreakdownResponse)
def dashboard_category_breakdown(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _: object = Depends(require_roles(RoleEnum.viewer, RoleEnum.analyst, RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> CategoryBreakdownResponse:
    return get_category_breakdown(db, date_from=date_from, date_to=date_to)


@router.get("/trends", response_model=TrendResponse)
def dashboard_trends(
    period: TrendPeriodEnum = Query(default=TrendPeriodEnum.monthly),
    type: TrendTypeFilterEnum = Query(default=TrendTypeFilterEnum.all),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _: object = Depends(require_roles(RoleEnum.viewer, RoleEnum.analyst, RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> TrendResponse:
    return get_trends(
        db,
        period=period,
        type_filter=type,
        date_from=date_from,
        date_to=date_to,
    )
