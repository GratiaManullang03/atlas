from typing import Optional, List 
from fastapi import Depends, HTTPException, status, Header
import re
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis

from app.core.security import verify_token
from app.db.session import get_db
from app.core.config import settings
from app.services.user_role import UserRoleService

# Optional: Redis dependency
def get_redis() -> Optional[redis.Redis]:
    """Get Redis connection (optional)"""
    try:
        if settings.REDIS_URL:
            return redis.from_url(settings.REDIS_URL, decode_responses=True)
    except ImportError:
        return None
    return None

# JWT Bearer token
security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """Get current user from JWT token"""
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        return None
    
    # Return user info dari token
    return {
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "email": payload.get("email"),
        "status": payload.get("status"),
    }

def require_auth(
    current_user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """Require authenticated user"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    def __call__(
        self,
        db: Session = Depends(get_db),
        user: dict = Depends(require_auth)
    ) -> None:
        user_id = user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials for permission check"
            )
        
        user_role_service = UserRoleService()
        user_permissions = user_role_service.get_user_permissions(db, int(user_id))
        
        # Super admin check
        if "*" in user_permissions:
            return
            
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Requires: {self.required_permission}"
            )
        
def validate_tenant_schema(schema_name: str = Header(None, alias="X-Tenant-Schema")):
    """Validate tenant schema name"""
    if schema_name and not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{0,62}$', schema_name):
        raise HTTPException(
            status_code=400,
            detail="Invalid schema name format. Must start with letter, contain only alphanumeric characters and underscores, and be 63 characters or less"
        )
    return schema_name or settings.DEFAULT_SCHEMA

def require_app_access(app_code: str):
    def _require_app_access(
        db: Session = Depends(get_db),
        current_user: dict = Depends(require_auth)
    ):
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials for permission check"
            )

        user_role_service = UserRoleService()
        user_roles = user_role_service.get_user_roles(db, int(user_id))

        if any(role.app_code == settings.APP_NAME and role.role_code == "SUPER_ADMIN" for role in user_roles):
            return

        if not any(role.app_code == app_code for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Requires access to application: {app_code}"
            )
    return _require_app_access

def require_role_level(allowed_levels: List[int]):
    """
    Dependency to check if the user has one of the allowed role levels for the current app.
    """
    def _require_role_level(
        db: Session = Depends(get_db),
        current_user: dict = Depends(require_auth)
    ):
        user_id = current_user.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials for permission check"
            )
        user_role_service = UserRoleService()
        user_roles = user_role_service.get_user_roles(db, int(user_id))

        # Cek apakah ada peran dalam aplikasi saat ini (ATLAS) yang levelnya diizinkan
        has_access = any(
            role.app_code == settings.APP_NAME and role.role_level in allowed_levels
            for role in user_roles
        )
        
        # Super admin selalu punya akses
        is_super_admin = any(
            role.app_code == settings.APP_NAME and role.role_code == "SUPER_ADMIN"
            for role in user_roles
        )

        if not has_access and not is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden. Required role level: {', '.join(map(str, allowed_levels))}"
            )
            
    return _require_role_level