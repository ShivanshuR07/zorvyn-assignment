from __future__ import annotations

from collections.abc import Generator
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.errors import forbidden, unauthorized
from app.core.security import decode_token
from app.models.user import User
from app.utils.enums import RoleEnum, UserStateEnum

from app.core.database import get_session_factory


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise unauthorized("Invalid authentication payload.")
    try:
        parsed_user_id = UUID(str(user_id))
    except ValueError as exc:
        raise unauthorized("Invalid authentication payload.") from exc
    user = db.get(User, parsed_user_id)
    if user is None:
        raise unauthorized("Authenticated user was not found.")
    if not user.is_active or user.state != UserStateEnum.active:
        raise unauthorized("Only active users can access protected resources.")
    return user


def require_roles(*roles: RoleEnum):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise forbidden()
        return current_user

    return dependency
