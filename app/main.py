from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import textwrap

from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=f"{settings.APP_NAME} - Atams Login & Authentication Service",
    version=settings.APP_VERSION,
    description = textwrap.dedent("""
        ATLAS is a multi-tenant authentication and authorization service.

        ## Features

        * **Authentication**: JWT-based login/logout with refresh tokens
        * **User Management**: Complete CRUD operations for users
        * **Application Management**: Manage applications within tenants
        * **Role Management**: Define roles with permissions per application
        * **User Role Assignment**: Assign/revoke roles to/from users
        * **Multi-Tenant**: Support for multiple tenant schemas

        ## Headers

        * **X-Tenant-Schema**: Specify tenant schema for multi-tenant operations
        * **Authorization**: Bearer token for authenticated requests
    """),
    openapi_url=f"/openapi.json" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure sesuai kebutuhan
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def read_root():
    """
    Welcome endpoint untuk ATLAS API.
    Memberikan informasi dasar tentang service.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} - Atams Login & Authentication Service",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "features": [
            "JWT Authentication",
            "User Management",
            "Application Management", 
            "Role-Based Access Control",
            "Multi-Tenant Support"
        ]
    }

# Include routers
app.include_router(api_router, prefix="/api/v1")