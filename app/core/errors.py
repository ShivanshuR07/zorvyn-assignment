from __future__ import annotations

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.requests import Request


class APIError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


def bad_request(message: str) -> APIError:
    return APIError(status.HTTP_400_BAD_REQUEST, "bad_request", message)


def unauthorized(message: str = "Authentication is required.") -> APIError:
    return APIError(status.HTTP_401_UNAUTHORIZED, "unauthorized", message)


def forbidden(message: str = "You do not have permission to perform this action.") -> APIError:
    return APIError(status.HTTP_403_FORBIDDEN, "forbidden", message)


def not_found(message: str) -> APIError:
    return APIError(status.HTTP_404_NOT_FOUND, "not_found", message)


def conflict(message: str) -> APIError:
    return APIError(status.HTTP_409_CONFLICT, "conflict", message)


def validation_error_response(exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "errors": exc.errors(),
            }
        },
    )


async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        payload = detail
    else:
        payload = {"code": "http_error", "message": str(detail)}
    return JSONResponse(status_code=exc.status_code, content={"detail": payload})


async def request_validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return validation_error_response(exc)


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred.",
            }
        },
    )


async def db_operational_error_handler(_: Request, exc: OperationalError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": {
                "code": "database_unavailable",
                "message": "Database connection failed. Check DATABASE_URL and PostgreSQL credentials.",
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(OperationalError, db_operational_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
