from fastapi import APIRouter

from app.api.v1.endpoints import health, auth, users, applications, roles, tenants

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenant-management"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
