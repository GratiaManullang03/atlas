from typing import Dict, Any
from pydantic import BaseModel

class PermissionsUpdate(BaseModel):
    """Schema for updating permissions on a role."""
    permissions: Dict[str, Any]