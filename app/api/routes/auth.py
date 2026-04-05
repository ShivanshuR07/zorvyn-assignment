from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import authenticate_user, build_login_response


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, email=payload.email, password=payload.password)
    return build_login_response(user)


@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_user)) -> UserRead:
    return current_user
