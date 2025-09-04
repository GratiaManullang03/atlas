from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.user import User

class ApplicationInfo(BaseModel):
    """Basic application info for role details"""
    model_config = ConfigDict(from_attributes=True)
    
    app_id: int
    app_code: str
    app_name: str
    app_description: Optional[str] = None

class RoleBase(BaseModel):
    r_app_id: int
    r_code: str
    r_name: str
    r_level: int = 0
    r_permissions: Optional[Dict[str, Any]]

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    r_code: Optional[str]
    r_name: Optional[str]
    r_level: Optional[int]
    r_permissions: Optional[Dict[str, Any]]

class RoleInDB(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    
    r_id: int
    created_at: datetime
    updated_at: Optional[datetime]

class Role(RoleInDB):
    pass

class RoleWithDetails(RoleInDB):
    """Role with application info and assigned users"""
    application: ApplicationInfo
    users: List[User] = []