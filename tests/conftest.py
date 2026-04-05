from __future__ import annotations

from collections.abc import Generator
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.database import Base
from app.core.security import hash_password
from app.main import create_app
from app.models.financial_record import FinancialRecord
from app.models.user import User
from app.utils.enums import RecordTypeEnum, RoleEnum, UserStateEnum


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        admin = User(
            full_name="Admin User",
            email="admin@example.com",
            password_hash=hash_password("admin1234"),
            role=RoleEnum.admin,
            state=UserStateEnum.active,
            is_active=True,
        )
        analyst = User(
            full_name="Analyst User",
            email="analyst@example.com",
            password_hash=hash_password("analyst1234"),
            role=RoleEnum.analyst,
            state=UserStateEnum.active,
            is_active=True,
        )
        viewer = User(
            full_name="Viewer User",
            email="viewer@example.com",
            password_hash=hash_password("viewer1234"),
            role=RoleEnum.viewer,
            state=UserStateEnum.active,
            is_active=True,
        )
        inactive = User(
            full_name="Inactive User",
            email="inactive@example.com",
            password_hash=hash_password("inactive1234"),
            role=RoleEnum.viewer,
            state=UserStateEnum.inactive,
            is_active=False,
        )
        session.add_all([admin, analyst, viewer, inactive])
        session.flush()
        session.add_all(
            [
                FinancialRecord(
                    amount=Decimal("1000.00"),
                    type=RecordTypeEnum.income,
                    category="salary",
                    record_date=date(2026, 4, 1),
                    notes="Salary",
                    created_by=admin.id,
                ),
                FinancialRecord(
                    amount=Decimal("300.00"),
                    type=RecordTypeEnum.expense,
                    category="food",
                    record_date=date(2026, 4, 2),
                    notes="Groceries",
                    created_by=admin.id,
                ),
            ]
        )
        session.commit()
        yield session


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
