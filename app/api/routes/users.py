from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User
from app.policies.user_policy import can_view_user
from app.schemas.user import UserCreate, UserListResponse, UserRead, UserStateUpdate, UserUpdate
from app.services.user_service import (
    create_user,
    delete_user,
    get_user_or_404,
    list_users,
    update_user,
    update_user_state,
)
from app.utils.enums import RoleEnum


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
def get_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> UserListResponse:
    items, total = list_users(db, limit=limit, offset=offset)
    return UserListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    payload: UserCreate,
    _: User = Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> UserRead:
    return create_user(db, payload)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    user = get_user_or_404(db, user_id)
    if not can_view_user(current_user, user_id):
        from app.core.errors import forbidden

        raise forbidden()
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user_endpoint(
    user_id: str,
    payload: UserUpdate,
    _: User = Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> UserRead:
    user = get_user_or_404(db, user_id)
    return update_user(db, user, payload)


@router.patch("/{user_id}/state", response_model=UserRead)
def update_user_state_endpoint(
    user_id: str,
    payload: UserStateUpdate,
    _: User = Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> UserRead:
    user = get_user_or_404(db, user_id)
    return update_user_state(db, user, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
    user_id: str,
    _: User = Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
) -> Response:
    user = get_user_or_404(db, user_id)
    delete_user(db, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
