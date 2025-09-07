from fastapi import APIRouter, Depends
from app.api.deps import require_app_access, require_role_level 
from app.core.config import settings

from app.api.v1.endpoints import health, auth, users, applications, roles, tenants

api_router = APIRouter()

# Dependency untuk memastikan pengguna punya akses ke aplikasi ATLAS
require_atlas_access = require_app_access(settings.APP_NAME) 

# Dependency untuk role level yang sangat tinggi (misal: Super Admin)
require_super_admin_level = require_role_level([100]) 

# Dependency untuk role level admin ke atas
require_admin_level = require_role_level([1000, 800, 10000]) 

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Contoh: Tenants hanya bisa diakses oleh level 100 (Super Admin)
api_router.include_router(
    tenants.router, 
    prefix="/tenants", 
    tags=["tenant-management"], 
    dependencies=[Depends(require_atlas_access), Depends(require_super_admin_level)]
)

api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["users"], 
    dependencies=[Depends(require_atlas_access), Depends(require_admin_level)]
)
api_router.include_router(
    applications.router, 
    prefix="/applications", 
    tags=["applications"], 
    dependencies=[Depends(require_atlas_access), Depends(require_admin_level)]
)
api_router.include_router(
    roles.router, 
    prefix="/roles", 
    tags=["roles"], 
    dependencies=[Depends(require_atlas_access), Depends(require_admin_level)]
)