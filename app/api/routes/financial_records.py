from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.user import User
from app.schemas.financial_record import (
    FinancialRecordCreate,
    FinancialRecordListResponse,
    FinancialRecordRead,
    FinancialRecordUpdate,
)
from app.services.financial_record_service import (
    create_record,
    delete_record,
    get_record_or_404,
    list_records,
    update_record,
)
from app.utils.enums import RecordTypeEnum, RoleEnum


router = APIRouter(prefix="/financial-records", tags=["Financial Records"])


@router.get("", response_model=FinancialRecordListResponse)
def get_financial_records(
    type: RecordTypeEnum | None = Query(default=None),
    category: str | None = Query(default=None, min_length=1, max_length=100),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles(RoleEnum.analyst, RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> FinancialRecordListResponse:
    items, total = list_records(
        db,
        record_type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return FinancialRecordListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=FinancialRecordRead, status_code=status.HTTP_201_CREATED)
def create_financial_record(
    payload: FinancialRecordCreate,
    current_user: User = Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> FinancialRecordRead:
    return create_record(db, payload, created_by=current_user.id)


@router.get("/{record_id}", response_model=FinancialRecordRead)
def get_financial_record(
    record_id: str,
    _: User = Depends(require_roles(RoleEnum.analyst, RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> FinancialRecordRead:
    return get_record_or_404(db, record_id)


@router.patch("/{record_id}", response_model=FinancialRecordRead)
def update_financial_record(
    record_id: str,
    payload: FinancialRecordUpdate,
    _: User = Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> FinancialRecordRead:
    record = get_record_or_404(db, record_id)
    return update_record(db, record, payload)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_financial_record(
    record_id: str,
    _: User = Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> Response:
    record = get_record_or_404(db, record_id)
    delete_record(db, record)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
