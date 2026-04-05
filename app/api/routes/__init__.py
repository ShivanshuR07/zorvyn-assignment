from fastapi import APIRouter

from app.api.routes import auth, dashboard, financial_records, reports, roles, users


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(financial_records.router)
api_router.include_router(reports.router)
