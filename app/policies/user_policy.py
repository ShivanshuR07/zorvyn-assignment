from app.models.user import User
from app.utils.enums import RoleEnum


def can_manage_users(current_user: User) -> bool:
    return current_user.role == RoleEnum.admin


def can_view_user(current_user: User, target_user_id: str) -> bool:
    return current_user.role == RoleEnum.admin or str(current_user.id) == str(target_user_id)
