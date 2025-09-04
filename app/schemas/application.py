from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user import User

class ApplicationBase(BaseModel):
    app_code: str
    app_name: str
    app_description: Optional[str]

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    app_code: Optional[str]
    app_name: Optional[str]
    app_description: Optional[str]

class ApplicationInDB(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    
    app_id: int
    created_at: datetime
    updated_at: Optional[datetime]

class RoleWithUsers(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    r_id: int
    r_code: str
    r_name: str
    users: List[User]

class ApplicationWithRoles(ApplicationInDB):
    roles: List[RoleWithUsers]

class Application(ApplicationInDB):
    pass