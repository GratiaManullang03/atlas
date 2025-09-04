from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List


class UserRoleAssignRequest(BaseModel):
    role_id: int


class UserRoleAssignBulkRequest(BaseModel):
    role_ids: List[int]


class UserRoleInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    ur_id: int
    ur_user_id: int
    ur_role_id: int
    created_at: datetime


class UserRole(UserRoleInDB):
    pass


class UserRoleWithDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    ur_id: int
    role_id: int
    role_code: str
    role_name: str
    role_level: int
    app_id: int
    app_name: str
    app_code: str
    created_at: datetime