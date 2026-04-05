from sqlalchemy.orm import Session

from app.core.errors import unauthorized
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserSummary
from app.utils.enums import UserStateEnum


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if user is None or not verify_password(password, user.password_hash):
        raise unauthorized("Invalid email or password.")
    if not user.is_active or user.state != UserStateEnum.active:
        raise unauthorized("Only active users can authenticate.")
    return user


def build_login_response(user: User) -> TokenResponse:
    token = create_access_token(
        subject=str(user.id),
        email=user.email,
        role=user.role,
        state=user.state,
    )
    return TokenResponse(access_token=token, user=UserSummary.model_validate(user))
