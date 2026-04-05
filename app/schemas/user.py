from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.utils.enums import RoleEnum, UserStateEnum


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    role: RoleEnum
    state: UserStateEnum
    is_active: bool


class UserRead(UserSummary):
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: RoleEnum = RoleEnum.viewer
    state: UserStateEnum = UserStateEnum.active

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Full name must not be empty.")
        return normalized


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: RoleEnum | None = None
    state: UserStateEnum | None = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Full name must not be empty.")
        return normalized


class UserStateUpdate(BaseModel):
    state: UserStateEnum


class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int
    limit: int
    offset: int


class RoleRead(BaseModel):
    name: RoleEnum
    permissions: list[str]
