from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import bad_request, not_found
from app.models.financial_record import FinancialRecord
from app.schemas.financial_record import FinancialRecordCreate, FinancialRecordUpdate
from app.utils.enums import RecordTypeEnum


def build_record_filters(
    query,
    *,
    record_type: RecordTypeEnum | None,
    category: str | None,
    date_from: date | None,
    date_to: date | None,
):
    if record_type is not None:
        query = query.filter(FinancialRecord.type == record_type)
    if category:
        query = query.filter(FinancialRecord.category.ilike(category.strip()))
    if date_from:
        query = query.filter(FinancialRecord.record_date >= date_from)
    if date_to:
        query = query.filter(FinancialRecord.record_date <= date_to)
    return query


def list_records(
    db: Session,
    *,
    record_type: RecordTypeEnum | None,
    category: str | None,
    date_from: date | None,
    date_to: date | None,
    limit: int,
    offset: int,
) -> tuple[list[FinancialRecord], int]:
    if date_from and date_to and date_from > date_to:
        raise bad_request("date_from must be earlier than or equal to date_to.")
    base_query = db.query(FinancialRecord).order_by(
        FinancialRecord.record_date.desc(),
        FinancialRecord.created_at.desc(),
    )
    filtered_query = build_record_filters(
        base_query,
        record_type=record_type,
        category=category,
        date_from=date_from,
        date_to=date_to,
    )
    total = filtered_query.count()
    records = filtered_query.offset(offset).limit(limit).all()
    return records, total


def get_record_or_404(db: Session, record_id: str) -> FinancialRecord:
    try:
        parsed_record_id = UUID(str(record_id))
    except ValueError as exc:
        raise bad_request("Invalid record id.") from exc
    record = db.get(FinancialRecord, parsed_record_id)
    if record is None:
        raise not_found("Financial record not found.")
    return record


def create_record(db: Session, payload: FinancialRecordCreate, *, created_by: Any) -> FinancialRecord:
    record = FinancialRecord(
        amount=payload.amount,
        type=payload.type,
        category=payload.category.strip(),
        record_date=payload.record_date,
        notes=payload.notes,
        created_by=created_by,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(db: Session, record: FinancialRecord, payload: FinancialRecordUpdate) -> FinancialRecord:
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record: FinancialRecord) -> None:
    db.delete(record)
    db.commit()
