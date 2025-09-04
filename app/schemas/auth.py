from typing import Optional, List
from pydantic import BaseModel, EmailStr
from app.schemas.user_role import UserRoleWithDetails

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LogoutRequest(BaseModel):
    refresh_token: str

class UserInfo(BaseModel):
    u_id: int
    u_username: str
    u_email: str
    u_full_name: Optional[str] = None
    u_status: str
    u_email_verified: bool
    roles: List[UserRoleWithDetails] = []

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class RequestEmailVerificationRequest(BaseModel):
    email: EmailStr