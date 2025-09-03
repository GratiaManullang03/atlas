from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_tenant_db as get_db
from app.api.deps import PermissionChecker
from app.services.role import RoleService
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.schemas.permission import PermissionsUpdate
from app.schemas.common import DataResponse, PaginationResponse

router = APIRouter()
role_service = RoleService()


@router.get("/", response_model=PaginationResponse[Role])
def get_roles(
    app_id: Optional[int] = Query(None, description="Filter by application ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(require_auth)  # Uncomment untuk require auth
):
    """Get list of roles with pagination and optional filtering by application"""
    roles = role_service.get_roles(db, app_id=app_id, skip=skip, limit=limit)
    total = role_service.get_total_roles(db, app_id=app_id)
    
    return PaginationResponse(
        success=True,
        message="Roles retrieved successfully",
        data=roles,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{role_id}", response_model=DataResponse[Role])
def get_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Get single role by ID"""
    role = role_service.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return DataResponse(
        success=True,
        message="Role retrieved successfully",
        data=role
    )


@router.post("/", response_model=DataResponse[Role])
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db)
):
    """Create new role"""
    new_role = role_service.create_role(db, role)
    
    if not new_role:
        raise HTTPException(
            status_code=400, 
            detail="Application not found or role code already exists for this application"
        )
    
    return DataResponse(
        success=True,
        message="Role created successfully",
        data=new_role
    )


@router.put("/{role_id}", response_model=DataResponse[Role])
def update_role(
    role_id: int,
    role: RoleUpdate,
    db: Session = Depends(get_db)
):
    """Update existing role"""
    updated_role = role_service.update_role(db, role_id, role)
    
    if not updated_role:
        raise HTTPException(
            status_code=400, 
            detail="Role not found or role code already exists for this application"
        )
    
    return DataResponse(
        success=True,
        message="Role updated successfully",
        data=updated_role
    )


@router.delete("/{role_id}", response_model=DataResponse[None])
def delete_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Delete role"""
    deleted = role_service.delete_role(db, role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return DataResponse(
        success=True,
        message="Role deleted successfully",
        data=None
    )

@router.put("/{role_id}/permissions", response_model=DataResponse[Role])
def update_permissions_for_role(
    role_id: int,
    permissions_data: PermissionsUpdate,
    db: Session = Depends(get_db),
    # Lindungi endpoint ini, hanya yang punya izin boleh mengakses
    _: dict = Depends(PermissionChecker("roles:update_permissions"))
):
    """Update permissions for a role."""
    updated_role = role_service.update_role_permissions(
        db, role_id, permissions_data.permissions
    )

    if not updated_role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )
    
    return DataResponse(
        success=True,
        message="Role permissions updated successfully",
        data=updated_role
    )