from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import PermissionChecker
from app.services.user import UserService
from app.services.user_role import UserRoleService
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.user_role import (
    UserRoleAssignBulkRequest, 
    UserRoleWithDetails
)
from app.schemas.common import DataResponse, PaginationResponse
from app.api.deps import require_auth
from app.schemas.auth import UserInfo

router = APIRouter()
user_service = UserService()
user_role_service = UserRoleService()

@router.get("/", response_model=PaginationResponse[User])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: dict = Depends(PermissionChecker("users:read"))
    # current_user: dict = Depends(require_auth)  # Uncomment untuk require auth
):
    """Get list of users with pagination"""
    users = user_service.get_users(db, skip=skip, limit=limit)
    total = user_service.get_total_users(db)
    
    return PaginationResponse(
        success=True,
        message="Users retrieved successfully",
        data=users,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{user_id}", response_model=DataResponse[User])
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(PermissionChecker("users:read"))
):
    """Get single user by ID"""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return DataResponse(
        success=True,
        message="User retrieved successfully",
        data=user
    )

@router.post("/", response_model=DataResponse[User])
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(PermissionChecker("users:read"))
):
    """Create new user"""
    new_user = user_service.create_user(db, user)
    
    if not new_user:
        raise HTTPException(
            status_code=400, 
            detail="Username or email already exists"
        )
    
    return DataResponse(
        success=True,
        message="User created successfully",
        data=new_user
    )

@router.put("/{user_id}", response_model=DataResponse[User])
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(PermissionChecker("users:read"))
):
    """Update existing user"""
    updated_user = user_service.update_user(db, user_id, user)
    
    if not updated_user:
        raise HTTPException(
            status_code=400, 
            detail="User not found or username/email already exists"
        )
    
    return DataResponse(
        success=True,
        message="User updated successfully",
        data=updated_user
    )

@router.delete("/{user_id}", response_model=DataResponse[None])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth) # Dapatkan info user saat ini
):
    """Delete user"""
    # Teruskan informasi user ke service
    deleted = user_service.delete_user(db, user_id, current_user) 
    
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found or insufficient permissions")
    
    return DataResponse(
        success=True,
        message="User deleted successfully",
        data=None
    )

# User Role Management Endpoints
@router.post("/{user_id}/roles", response_model=DataResponse[List[UserRoleWithDetails]])
def assign_roles_to_user(
    user_id: int,
    role_request: UserRoleAssignBulkRequest,
    db: Session = Depends(get_db)
):
    """Assign multiple roles to user"""
    # Check if user exists
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Assign roles
    user_role_service.assign_roles_to_user(db, user_id, role_request.role_ids)
    
    # Return updated user roles
    user_roles = user_role_service.get_user_roles(db, user_id)
    
    return DataResponse(
        success=True,
        message="Roles assigned successfully",
        data=user_roles
    )

@router.get("/{user_id}/roles", response_model=DataResponse[List[UserRoleWithDetails]])
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all roles assigned to user"""
    # Check if user exists
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_roles = user_role_service.get_user_roles(db, user_id)
    
    return DataResponse(
        success=True,
        message="User roles retrieved successfully",
        data=user_roles
    )

@router.delete("/{user_id}/roles/{role_id}", response_model=DataResponse[None])
def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db)
):
    """Remove role from user"""
    # Check if user exists
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    removed = user_role_service.remove_role_from_user(db, user_id, role_id)
    
    if not removed:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    
    return DataResponse(
        success=True,
        message="Role removed from user successfully",
        data=None
    )