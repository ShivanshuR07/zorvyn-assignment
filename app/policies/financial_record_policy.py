from app.models.user import User
from app.utils.enums import RoleEnum


def can_read_records(current_user: User) -> bool:
    return current_user.role in {RoleEnum.viewer, RoleEnum.analyst, RoleEnum.admin}


def can_create_record(current_user: User) -> bool:
    return current_user.role == RoleEnum.admin


def can_update_record(current_user: User) -> bool:
    return current_user.role == RoleEnum.admin


def can_delete_record(current_user: User) -> bool:
    return current_user.role == RoleEnum.admin
