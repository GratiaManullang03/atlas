from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


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