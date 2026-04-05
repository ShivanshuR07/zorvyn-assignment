from pydantic import BaseModel, EmailStr

from app.schemas.user import UserSummary


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPayload(BaseModel):
    sub: str
    email: EmailStr
    role: str
    state: str
    exp: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary
