from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import get_session_factory
from app.core.security import hash_password
from app.models.financial_record import FinancialRecord
from app.models.user import User
from app.utils.enums import RecordTypeEnum, RoleEnum, UserStateEnum


def _seed_users(session: Session) -> dict[str, User]:
    users_by_email = {user.email: user for user in session.query(User).all()}
    seed_specs = [
        {
            "full_name": "Shivanshu",
            "email": "shivanshu@example.com",
            "password": "shivanshu123",
            "role": RoleEnum.admin,
            "state": UserStateEnum.active,
        },
        {
            "full_name": "Aditi Sharma",
            "email": "aditi@example.com",
            "password": "aditi1234",
            "role": RoleEnum.analyst,
            "state": UserStateEnum.active,
        },
        {
            "full_name": "Rahul Mehta",
            "email": "rahul@example.com",
            "password": "rahul1234",
            "role": RoleEnum.viewer,
            "state": UserStateEnum.active,
        },
        {
            "full_name": "Neha Kapoor",
            "email": "neha@example.com",
            "password": "neha1234",
            "role": RoleEnum.analyst,
            "state": UserStateEnum.inactive,
        },
    ]

    created_users: dict[str, User] = {}
    for spec in seed_specs:
        user = users_by_email.get(spec["email"])
        is_active = spec["state"] == UserStateEnum.active
        if user is None:
            user = User(
                full_name=spec["full_name"],
                email=spec["email"],
                password_hash=hash_password(spec["password"]),
                role=spec["role"],
                state=spec["state"],
                is_active=is_active,
            )
            session.add(user)
        else:
            user.full_name = spec["full_name"]
            user.password_hash = hash_password(spec["password"])
            user.role = spec["role"]
            user.state = spec["state"]
            user.is_active = is_active
        created_users[spec["email"]] = user

    session.flush()
    return created_users


def _seed_records(session: Session, users: dict[str, User]) -> int:
    if session.query(FinancialRecord).count() > 0:
        return 0

    rng = random.Random(42)
    today = date.today()
    active_users = [user for user in users.values() if user.is_active]

    categories = {
        RecordTypeEnum.income: ["salary", "freelance", "investment", "bonus"],
        RecordTypeEnum.expense: ["rent", "food", "travel", "utilities", "shopping", "health"],
    }
    notes_pool = [
        "Monthly recurring entry",
        "Imported from dashboard seed data",
        "Manual finance adjustment",
        "Quarterly review input",
        "Frontend test dataset",
    ]

    records: list[FinancialRecord] = []
    for _ in range(56):
        record_type = rng.choice([RecordTypeEnum.income, RecordTypeEnum.expense])
        category = rng.choice(categories[record_type])
        amount = Decimal(str(round(rng.uniform(250, 18000), 2)))
        records.append(
            FinancialRecord(
                amount=amount,
                type=record_type,
                category=category,
                record_date=today - timedelta(days=rng.randint(0, 180)),
                notes=rng.choice(notes_pool),
                created_by=active_users[rng.randrange(len(active_users))].id,
            )
        )

    shivanshu = users["shivanshu@example.com"]
    records.extend(
        [
            FinancialRecord(
                amount=Decimal("95000.00"),
                type=RecordTypeEnum.income,
                category="salary",
                record_date=today.replace(day=1),
                notes="Primary monthly salary",
                created_by=shivanshu.id,
            ),
            FinancialRecord(
                amount=Decimal("12000.00"),
                type=RecordTypeEnum.income,
                category="freelance",
                record_date=today.replace(day=min(today.day, 10)),
                notes="Weekend consulting payout",
                created_by=shivanshu.id,
            ),
            FinancialRecord(
                amount=Decimal("18000.00"),
                type=RecordTypeEnum.expense,
                category="rent",
                record_date=today.replace(day=min(today.day, 5)),
                notes="House rent payment",
                created_by=shivanshu.id,
            ),
            FinancialRecord(
                amount=Decimal("4200.50"),
                type=RecordTypeEnum.expense,
                category="food",
                record_date=today.replace(day=min(today.day, 8)),
                notes="Groceries and dining",
                created_by=shivanshu.id,
            ),
        ]
    )

    session.add_all(records)
    return len(records)


def main() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        users = _seed_users(session)
        created_records = _seed_records(session, users)
        session.commit()

    print("Seed complete.")
    print("Admin login:")
    print("  email: shivanshu@example.com")
    print("  password: shivanshu123")
    print(f"Created or refreshed {len(users)} users.")
    print(f"Inserted {created_records} financial records.")


if __name__ == "__main__":
    main()
