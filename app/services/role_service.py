from app.core.errors import not_found
from app.schemas.user import RoleRead
from app.utils.enums import RoleEnum


ROLE_PERMISSIONS: dict[RoleEnum, list[str]] = {
    RoleEnum.viewer: [
        "auth:login",
        "auth:me",
        "dashboard:read",
    ],
    RoleEnum.analyst: [
        "auth:login",
        "auth:me",
        "dashboard:read",
        "financial_records:read",
        "reports:read",
    ],
    RoleEnum.admin: [
        "auth:login",
        "auth:me",
        "dashboard:read",
        "users:manage",
        "roles:read",
        "financial_records:manage",
        "reports:read",
    ],
}


def list_roles() -> list[RoleRead]:
    return [RoleRead(name=role, permissions=permissions) for role, permissions in ROLE_PERMISSIONS.items()]


def get_role(role_name: RoleEnum) -> RoleRead:
    permissions = ROLE_PERMISSIONS.get(role_name)
    if permissions is None:
        raise not_found("Role not found.")
    return RoleRead(name=role_name, permissions=permissions)
