# API Documentation

## Overview

Base behavior:

- REST-style resource routes
- JSON request and response bodies
- JWT Bearer auth on protected routes
- role-based access enforced in dependencies
- consistent error shape

Common error response:

```json
{
  "detail": {
    "code": "forbidden",
    "message": "You do not have permission to perform this action."
  }
}
```

## Response Codes

Common codes used by the API:

- `200 OK` for successful reads and updates
- `201 Created` for successful creates
- `204 No Content` for successful deletes
- `400 Bad Request` for malformed IDs or invalid date ranges
- `401 Unauthorized` for invalid credentials or invalid/missing token
- `403 Forbidden` for valid user without required role
- `404 Not Found` for missing user, role, or financial record
- `409 Conflict` for duplicate user email or conflicting updates
- `422 Unprocessable Entity` for request validation failures
- `500 Internal Server Error` for unexpected server errors

## Health

### `GET /health`

Purpose:

- basic service health check

Auth:

- public

Success response:

- `200 OK`

Example:

```json
{
  "status": "ok"
}
```

## Dashboard Routes

Dashboard routes are viewer-safe, derived read-only endpoints.

### `GET /dashboard/summary`

Auth:

- `viewer`
- `analyst`
- `admin`

Purpose:

- expose top-level dashboard totals without exposing raw record listings

### `GET /dashboard/category-breakdown`

Auth:

- `viewer`
- `analyst`
- `admin`

Purpose:

- expose grouped category totals for dashboard cards and charts

### `GET /dashboard/trends`

Auth:

- `viewer`
- `analyst`
- `admin`

Purpose:

- expose dashboard trend series without granting record-level access

## Authentication Routes

### `POST /auth/login`

Purpose:

- authenticate a user with email and password
- issue a signed JWT access token

Auth:

- public

Request body:

```json
{
  "email": "shivanshu@example.com",
  "password": "shivanshu123"
}
```

Success:

- `200 OK`

Error cases:

- `401` invalid email or password
- `401` inactive or suspended user
- `422` malformed request payload

Business logic:

- email is normalized to lowercase
- password is verified against bcrypt hash
- user must have `state=active` and `is_active=true`
- JWT contains user identity and role context

### `GET /auth/me`

Purpose:

- return the currently authenticated user

Auth:

- any active authenticated user

Success:

- `200 OK`

Error cases:

- `401` missing token
- `401` invalid or expired token
- `401` token user missing or no longer active

Business logic:

- token is decoded
- `sub` is resolved to a user ID
- active-state check is re-applied on every request

## User Routes

### `GET /users`

Purpose:

- list users with pagination

Auth:

- `admin`

Query params:

- `limit`
- `offset`

Success:

- `200 OK`

Error cases:

- `401` unauthenticated
- `403` non-admin

Business logic:

- sorted by newest `created_at` first
- returns list metadata: `total`, `limit`, `offset`

### `POST /users`

Purpose:

- create a new user

Auth:

- `admin`

Success:

- `201 Created`

Error cases:

- `403` non-admin
- `409` duplicate email
- `422` invalid name, email, password, role, or state

Business logic:

- password is hashed before storage
- email is lowercased
- `is_active` is derived from state

### `GET /users/{user_id}`

Purpose:

- fetch a single user

Auth:

- `admin`
- or the same user requesting their own profile

Success:

- `200 OK`

Error cases:

- `400` malformed UUID
- `401` unauthenticated
- `403` other non-admin user tries to access someone else
- `404` user not found

Business logic:

- self-read is allowed
- all broader user management remains admin-only

### `PATCH /users/{user_id}`

Purpose:

- update mutable user fields

Auth:

- `admin`

Supported fields:

- `full_name`
- `password`
- `role`
- `state`

Success:

- `200 OK`

Error cases:

- `400` malformed UUID
- `403` non-admin
- `404` missing user
- `409` conflicting update
- `422` invalid payload

Business logic:

- password is re-hashed when provided
- state changes also synchronize `is_active`

### `PATCH /users/{user_id}/state`

Purpose:

- change only lifecycle state

Auth:

- `admin`

Success:

- `200 OK`

Error cases:

- `400`, `403`, `404`, `422`

Business logic:

- updates `state`
- recalculates `is_active`

## Role Routes

### `GET /roles`

Purpose:

- list the static role catalog and permissions

Auth:

- `admin`

Success:

- `200 OK`

Error cases:

- `401`
- `403`

Business logic:

- reads the in-code role-permission mapping
- intended mainly for admin tooling or frontend inspection

### `GET /roles/{role_name}`

Purpose:

- fetch a single role definition

Auth:

- `admin`

Success:

- `200 OK`

Error cases:

- `401`
- `403`
- `404` invalid role

## Financial Record Routes

### `GET /financial-records`

Purpose:

- list records with filters and pagination

Auth:

- `analyst`
- `admin`

Query params:

- `type`
- `category`
- `date_from`
- `date_to`
- `limit`
- `offset`

Success:

- `200 OK`

Error cases:

- `400` if `date_from > date_to`
- `401`
- `403`
- `422` invalid filter values

Business logic:

- sorted by `record_date DESC`, then `created_at DESC`
- category filter is case-insensitive
- returns list metadata for frontend pagination

### `POST /financial-records`

Purpose:

- create a new financial record

Auth:

- `admin`

Success:

- `201 Created`

Error cases:

- `401`
- `403`
- `422` invalid amount, type, category, date, or notes

Business logic:

- `created_by` is assigned from the authenticated admin
- amount must be non-negative
- record immediately becomes available to report endpoints

### `GET /financial-records/{record_id}`

Purpose:

- fetch a single record

Auth:

- `analyst`
- `admin`

Success:

- `200 OK`

Error cases:

- `400` malformed UUID
- `401`
- `403`
- `404` missing record

### `PATCH /financial-records/{record_id}`

Purpose:

- update an existing record

Auth:

- `admin`

Success:

- `200 OK`

Error cases:

- `400`
- `401`
- `403`
- `404`
- `422`

Business logic:

- partial update supported
- updated values immediately affect all reporting endpoints

### `DELETE /financial-records/{record_id}`

Purpose:

- delete a record

Auth:

- `admin`

Success:

- `204 No Content`

Error cases:

- `400`
- `401`
- `403`
- `404`

Business logic:

- hard delete in current version

## Report Routes

Reports are derived resources computed from `financial_records`.

### `GET /reports/summary`

Purpose:

- return `total_income`, `total_expense`, and `net_balance`

Auth:

- `analyst`
- `admin`

Query params:

- `date_from`
- `date_to`

Success:

- `200 OK`

Error cases:

- `400` invalid date range
- `401`
- `403`

Business logic:

- aggregates with SQL functions
- `net_balance = total_income - total_expense`

### `GET /reports/category-breakdown`

Purpose:

- return grouped totals by category and record type

Auth:

- `analyst`
- `admin`

Query params:

- `date_from`
- `date_to`

Success:

- `200 OK`

Error cases:

- `400`
- `401`
- `403`

Business logic:

- grouped by `category` and `type`
- sorted by highest total first

### `GET /reports/trends`

Purpose:

- return weekly or monthly aggregation series

Auth:

- `analyst`
- `admin`

Query params:

- `period=weekly|monthly`
- `type=income|expense|all`
- `date_from`
- `date_to`

Success:

- `200 OK`

Error cases:

- `400`
- `401`
- `403`
- `422`

Business logic:

- uses `date_trunc` on `record_date`
- always returns income, expense, and net values per bucket
- optional `type` filter narrows the source rows before aggregation

### `GET /reports/recent-activity`

Purpose:

- return latest records for dashboard widgets/activity feeds

Auth:

- `analyst`
- `admin`

Query params:

- `limit`
- `date_from`
- `date_to`

Success:

- `200 OK`

Error cases:

- `400`
- `401`
- `403`

Business logic:

- ordered by `record_date DESC`, then `created_at DESC`
- useful for lightweight frontend dashboard cards

## Access Matrix

| Route Group | Viewer | Analyst | Admin |
| --- | --- | --- | --- |
| `/auth/me` | Yes | Yes | Yes |
| `/dashboard/*` | Yes | Yes | Yes |
| `/users` | No | No | Yes |
| `/roles` | No | No | Yes |
| `GET /financial-records` | No | Yes | Yes |
| `POST/PATCH/DELETE /financial-records` | No | No | Yes |
| `/reports/*` | No | Yes | Yes |

## Implementation References

- [app/api/routes/auth.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/api/routes/auth.py)
- [app/api/routes/users.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/api/routes/users.py)
- [app/api/routes/roles.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/api/routes/roles.py)
- [app/api/routes/financial_records.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/api/routes/financial_records.py)
- [app/api/routes/reports.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/api/routes/reports.py)
