from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
    u_username: str
    u_email: EmailStr
    u_full_name: Optional[str]
    u_status: str = "active"

class UserCreate(UserBase):
    u_password: str
    u_email_verified: bool = False

class UserUpdate(BaseModel):
    u_username: Optional[str]
    u_email: Optional[EmailStr]
    u_full_name: Optional[str]
    u_status: Optional[str]
    u_email_verified: Optional[bool]
    u_password: Optional[str]

class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    u_id: int
    u_email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]

class User(UserInDB):
    pass