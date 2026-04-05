# Finance Dashboard Backend

Minimal but complete FastAPI backend for a finance dashboard. It is organized as a clean REST API with modular routing, service, and policy layers so you can plug in a frontend immediately without reworking backend structure.

## Stack

- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- JWT authentication with `python-jose`
- Password hashing with `passlib[bcrypt]`
- Pydantic validation
- Pytest for a small verification suite

## Project Structure

```text
app/
  main.py
  core/
  api/
  models/
  schemas/
  services/
  policies/
  utils/
alembic/
scripts/
tests/
```

## Features

- JWT login via `POST /auth/login`
- Current-user endpoint via `GET /auth/me`
- Admin-only user management
- Static role catalog via `GET /roles`
- Financial record CRUD with filters for type, category, and date range
- Read-only reporting endpoints for summary, category breakdown, trends, and recent activity
- Consistent error response shape
- Seed data including admin user `Shivanshu`

## Roles

- `viewer`: can authenticate and view dashboard data only
- `analyst`: can authenticate, read records, and access reports
- `admin`: full access to users, roles, records, and record edits

## Environment

Copy `.env.example` to `.env` and adjust values as needed.

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/finance_dashboard
JWT_SECRET_KEY=change-this-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
APP_ENV=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Important:

- if `.env` is missing, the backend falls back to `postgres:postgres@localhost:5432/finance_dashboard`
- if your local Postgres password is different, login requests will fail before auth logic runs because the API cannot open a database connection

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
alembic upgrade head
```

4. Seed local data:

```bash
python -m scripts.seed
```

5. Start the API:

```bash
uvicorn app.main:app --reload
```

API docs will be available at `http://localhost:8000/docs`.

## Frontend

The React frontend lives in [frontend/](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/frontend).

Setup:

```bash
cd frontend
npm install
```

Run the frontend alone:

```bash
npm run dev
```

Frontend default URL:

- `http://localhost:5173`

Frontend environment file:

- copy `frontend/.env.example` to `frontend/.env`
- default backend API base URL is `http://localhost:8000`

## Run Both Together

Use the launcher script from the repo root:

```bash
python run_full_stack.py
```

It starts:

- FastAPI on `http://localhost:8000`
- React frontend on `http://localhost:5173`

Press `Ctrl+C` to stop both.

## Local Env Helper

If you want a guided `.env` setup, run:

```bash
python setup_local_env.py
```

It will prompt for your PostgreSQL credentials and write the repo-root `.env` file for you.

## Seeded Login

- Email: `shivanshu@example.com`
- Password: `shivanshu123`
- Role: `admin`

## Main Endpoints

### Authentication

- `POST /auth/login`
- `GET /auth/me`

### Users

- `GET /users`
- `POST /users`
- `GET /users/{user_id}`
- `PATCH /users/{user_id}`
- `PATCH /users/{user_id}/state`

### Roles

- `GET /roles`
- `GET /roles/{role_name}`

### Financial Records

- `GET /financial-records`
- `POST /financial-records`
- `GET /financial-records/{record_id}`
- `PATCH /financial-records/{record_id}`
- `DELETE /financial-records/{record_id}`

### Reports

- `GET /reports/summary`
- `GET /reports/category-breakdown`
- `GET /reports/trends`
- `GET /reports/recent-activity`

## Notes for Frontend Integration

- All protected endpoints use `Authorization: Bearer <token>`.
- Responses are JSON-first and use stable resource-oriented routes.
- CORS origins are environment-driven so you can point the backend at your frontend dev server quickly.
- Role checks are centralized in dependencies and policy helpers, which keeps it easy to extend if your frontend later needs finer-grained access control.

## Tests

Run the test suite with:

```bash
pytest
```

## Detailed Documentation

- [docs/database.md](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/docs/database.md)
- [docs/api.md](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/docs/api.md)
- [docs/auth.md](/C:/Users/sh16i/OneDrive/Desktop/zorvyn/docs/auth.md)
