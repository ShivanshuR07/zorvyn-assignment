from fastapi import APIRouter, Depends

from app.api.deps import require_roles
from app.schemas.user import RoleRead
from app.services.role_service import get_role, list_roles
from app.utils.enums import RoleEnum


router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=list[RoleRead])
def get_roles(_: object = Depends(require_roles(RoleEnum.admin))) -> list[RoleRead]:
    return list_roles()


@router.get("/{role_name}", response_model=RoleRead)
def get_role_detail(
    role_name: RoleEnum,
    _: object = Depends(require_roles(RoleEnum.admin)),
) -> RoleRead:
    return get_role(role_name)
