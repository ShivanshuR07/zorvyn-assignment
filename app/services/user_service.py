from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import bad_request, conflict, not_found
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserStateUpdate, UserUpdate
from app.utils.enums import UserStateEnum


def state_is_active(state: UserStateEnum) -> bool:
    return state == UserStateEnum.active


def list_users(db: Session, *, limit: int, offset: int) -> tuple[list[User], int]:
    query = db.query(User).order_by(User.created_at.desc())
    total = query.count()
    users = query.offset(offset).limit(limit).all()
    return users, total


def get_user_or_404(db: Session, user_id: str) -> User:
    try:
        parsed_user_id = UUID(str(user_id))
    except ValueError as exc:
        raise bad_request("Invalid user id.") from exc
    user = db.get(User, parsed_user_id)
    if user is None:
        raise not_found("User not found.")
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def create_user(db: Session, payload: UserCreate) -> User:
    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        state=payload.state,
        is_active=state_is_active(payload.state),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("A user with this email already exists.") from exc
    db.refresh(user)
    return user


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    updates = payload.model_dump(exclude_unset=True)
    if "full_name" in updates:
        user.full_name = updates["full_name"]
    if "password" in updates:
        user.password_hash = hash_password(updates["password"])
    if "role" in updates:
        user.role = updates["role"]
    if "state" in updates:
        user.state = updates["state"]
        user.is_active = state_is_active(updates["state"])
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("Unable to update the user due to a conflicting value.") from exc
    db.refresh(user)
    return user


def update_user_state(db: Session, user: User, payload: UserStateUpdate) -> User:
    user.state = payload.state
    user.is_active = state_is_active(payload.state)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
