from app.models.user import User
from app.utils.enums import RoleEnum


def can_view_reports(current_user: User) -> bool:
    return current_user.role in {RoleEnum.analyst, RoleEnum.admin}
