# Authentication Documentation

## Overview

Authentication is JWT-based and stateless.

Current auth goals:

- identify the current user on each protected request
- enforce active-user checks
- enforce role-based authorization
- keep the backend ready for immediate frontend integration

Core files:

- [app/core/security.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/core/security.py)
- [app/api/deps.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/api/deps.py)
- [app/services/auth_service.py](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/app/services/auth_service.py)

## User Identity Model

Authentication is based on the `users` table.

Relevant user fields:

- `id`
- `email`
- `password_hash`
- `role`
- `state`
- `is_active`

These fields support:

- credential validation
- token issuance
- route-level authorization
- active-state enforcement

## Supported Roles

### `viewer`

- can log in
- can call `GET /auth/me`
- can access dashboard endpoints
- cannot read actual financial record listings
- cannot access reports
- cannot manage users
- cannot write records

### `analyst`

- can log in
- can call `GET /auth/me`
- can access dashboard endpoints
- can read financial records
- can access report endpoints
- cannot manage users
- cannot create, update, or delete records

### `admin`

- can log in
- can call `GET /auth/me`
- can access dashboard endpoints
- can manage users
- can inspect role definitions
- can create, update, and delete financial records
- can access reports

## Account State Rules

States:

- `active`
- `inactive`
- `suspended`

Authentication policy:

- only `active` users may authenticate
- `is_active` must also be `true`
- inactive or suspended users receive `401 Unauthorized`

Protected route policy:

- active-state validation is checked again on every protected request
- a user whose account becomes inactive after login will stop being authorized even if they still hold an old token

## Password Handling

Password storage:

- plaintext passwords are never stored
- `passlib` with `bcrypt` is used to hash passwords

Password verification:

- performed only during login
- the submitted password is checked against `password_hash`

Password update behavior:

- if an admin updates a user's password, the new value is re-hashed before save

## Token Model

The API issues a Bearer access token after successful login.

Response shape:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "full_name": "Shivanshu",
    "email": "shivanshu@example.com",
    "role": "admin",
    "state": "active",
    "is_active": true
  }
}
```

### JWT Claims

Current token payload includes:

- `sub`: user UUID
- `email`: normalized email
- `role`: current role
- `state`: current lifecycle state
- `exp`: expiration timestamp

Why these claims exist:

- `sub` identifies the user
- `role` and `state` allow lightweight request context
- `exp` limits token lifetime

Even with these claims, the backend still reloads the user from the database on protected requests to avoid trusting stale token state alone.

## Authentication Procedure

### Login Flow

1. Client sends `POST /auth/login` with `email` and `password`.
2. Backend looks up the user by normalized email.
3. Backend verifies the bcrypt password hash.
4. Backend checks `state == active` and `is_active == true`.
5. Backend signs a JWT using the configured secret and algorithm.
6. Backend returns the token plus safe user profile data.

### Authenticated Request Flow

1. Client sends `Authorization: Bearer <token>`.
2. Backend decodes and verifies the JWT signature.
3. Backend extracts `sub`.
4. Backend resolves the user from the database.
5. Backend confirms the user still exists and is active.
6. Role dependency checks determine whether the route is allowed.

## Authorization Dependencies

### `get_current_user`

Purpose:

- decode the Bearer token
- resolve the user by UUID
- reject inactive or missing users

Failure cases:

- malformed token
- expired token
- token without `sub`
- token pointing to a missing user
- inactive or suspended user

### `require_roles(...)`

Purpose:

- centralize role checks for protected routes

Examples:

- `require_roles("admin")`
- `require_roles("analyst", "admin")`
- `require_roles("viewer", "analyst", "admin")`

Result:

- raises `403 Forbidden` when the authenticated role is insufficient

## Endpoints

### `POST /auth/login`

Use when:

- the frontend wants to establish an authenticated session

Returns:

- Bearer access token
- current user summary

Error behavior:

- invalid credentials -> `401`
- inactive account -> `401`
- bad payload -> `422`

### `GET /auth/me`

Use when:

- frontend needs the logged-in user profile
- frontend wants to bootstrap role-aware UI
- frontend wants to validate a stored token

Returns:

- current user record without sensitive fields like password hash

## Frontend Usage Notes

Recommended frontend flow:

1. Login once with email/password.
2. Store the access token securely on the client.
3. Attach it to every protected request using `Authorization: Bearer <token>`.
4. Call `GET /auth/me` on app load to restore session state.
5. Use the returned `role` to conditionally show admin, analyst, or viewer UI.

UI behavior to expect:

- `401` should redirect to login or trigger token refresh strategy later
- `403` should show an authorization message, not a login prompt

## Configuration

Environment variables used by auth:

- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `JWT_EXPIRE_MINUTES`

Security note:

- `JWT_SECRET_KEY` must be different in real environments
- do not commit production secrets into the repo

## Seeded Login Accounts

Local seed script creates:

- admin: `shivanshu@example.com` / `shivanshu123`
- analyst: `aditi@example.com` / `aditi1234`
- viewer: `rahul@example.com` / `rahul1234`
- inactive analyst: `neha@example.com` / `neha1234`

Use the inactive account to verify that login rejection works as expected.
