"""Initial finance dashboard schema.

Revision ID: 20260405_0001
Revises:
Create Date: 2026-04-05 14:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260405_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("viewer", "analyst", "admin", name="user_role", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.Enum("active", "inactive", "suspended", name="user_state", native_enum=False),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "financial_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column(
            "type",
            sa.Enum("income", "expense", name="record_type", native_enum=False),
            nullable=False,
        ),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount >= 0", name=op.f("ck_financial_records_amount_non_negative")),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name=op.f("fk_financial_records_created_by_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_financial_records")),
    )
    op.create_index("ix_financial_records_type", "financial_records", ["type"], unique=False)
    op.create_index("ix_financial_records_category", "financial_records", ["category"], unique=False)
    op.create_index("ix_financial_records_record_date", "financial_records", ["record_date"], unique=False)
    op.create_index("ix_financial_records_created_by", "financial_records", ["created_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_financial_records_created_by", table_name="financial_records")
    op.drop_index("ix_financial_records_record_date", table_name="financial_records")
    op.drop_index("ix_financial_records_category", table_name="financial_records")
    op.drop_index("ix_financial_records_type", table_name="financial_records")
    op.drop_table("financial_records")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
