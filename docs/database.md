# Database Documentation

## Overview

The backend persists finance dashboard data in PostgreSQL through SQLAlchemy ORM models and Alembic migrations.

Persistent entities:

- `users`
- `financial_records`

Derived data:

- reports are computed from `financial_records`
- roles are static in application code, not stored in a table in the current version

## Schema Summary

### `users`

Purpose:

- stores application users
- stores role, lifecycle state, and password hash
- acts as the parent table for financial record ownership

Columns:

| Column | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `id` | `UUID` | No | Primary key |
| `full_name` | `VARCHAR(120)` | No | User display name |
| `email` | `VARCHAR(255)` | No | Unique login identifier |
| `password_hash` | `TEXT` | No | Bcrypt hash only, never plaintext |
| `role` | `ENUM(viewer, analyst, admin)` | No | Authorization role |
| `state` | `ENUM(active, inactive, suspended)` | No | Lifecycle state |
| `is_active` | `BOOLEAN` | No | Fast active/inactive check aligned to `state` |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | No | Last update timestamp |

Indexes and constraints:

- primary key on `id`
- unique index on `email`

Behavior notes:

- `email` is normalized to lowercase in service logic
- `state=active` implies `is_active=true`
- `state=inactive` or `state=suspended` implies `is_active=false`
- only active users can authenticate

### `financial_records`

Purpose:

- stores income and expense entries used by the dashboard
- supports CRUD, filtering, and reporting

Columns:

| Column | Type | Nullable | Notes |
| --- | --- | --- | --- |
| `id` | `UUID` | No | Primary key |
| `amount` | `NUMERIC(14,2)` | No | Must be non-negative |
| `type` | `ENUM(income, expense)` | No | Record direction |
| `category` | `VARCHAR(100)` | No | Used for filtering and aggregation |
| `record_date` | `DATE` | No | Business date of the record |
| `notes` | `TEXT` | Yes | Optional notes |
| `created_by` | `UUID` | No | FK to `users.id` |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | No | Last update timestamp |

Indexes and constraints:

- primary key on `id`
- check constraint: `amount >= 0`
- index on `type`
- index on `category`
- index on `record_date`
- index on `created_by`
- foreign key from `created_by` to `users.id`

Behavior notes:

- `type` determines whether a row contributes to income or expense reporting
- `record_date` is the main reporting date, not `created_at`
- `created_by` captures ownership/audit origin for seeded and admin-created records

## Relationships

### User to Financial Records

Cardinality:

- one user can create many financial records
- one financial record belongs to exactly one user

Foreign key:

- `financial_records.created_by -> users.id`

Delete behavior:

- `ON DELETE RESTRICT`
- a user cannot be removed if records still reference them

ORM relationship:

- `User.created_records`
- `FinancialRecord.created_by_user`

## Role Storage Model

Roles are not stored in a dedicated `roles` table in this version.

Current design:

- role values are stored directly on `users.role`
- role permissions are defined in application code
- `GET /roles` exposes the static catalog for frontend/API consumers

Why this is acceptable here:

- it keeps the backend minimal
- it matches the assignment requirement for a minimal implementation
- it is easy to evolve into a database-driven RBAC model later

## Reporting Data Model

Reports are computed, not persisted.

Current report sources:

- summary totals from `financial_records.amount`
- category totals grouped by `category` and `type`
- trend series grouped by week or month on `record_date`
- recent activity ordered by `record_date` and `created_at`

This keeps the backend modular for frontend integration because the frontend can call report endpoints directly without needing reporting tables.

## Migration Source

Initial schema migration:

- [alembic/versions/20260405_0001_initial_schema.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/alembic/versions/20260405_0001_initial_schema.py)

Key model files:

- [app/models/user.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/models/user.py)
- [app/models/financial_record.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/models/financial_record.py)

## Seeded Data

Seed script:

- [scripts/seed.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/scripts/seed.py)

Seeded users include:

- `Shivanshu` as `admin`
- one `analyst`
- one `viewer`
- one inactive user for auth testing

Seeded records include:

- both `income` and `expense`
- multiple categories
- multiple dates
- deterministic records for dashboard demonstrations
