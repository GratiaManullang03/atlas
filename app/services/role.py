from typing import Optional, List, Dict, Any, cast
from sqlalchemy.orm import Session

from app.repositories.role import RoleRepository
from app.repositories.application import ApplicationRepository
from app.schemas.role import Role, RoleCreate, RoleUpdate, RoleWithDetails, ApplicationInfo
from app.schemas.user import User

class RoleService:
    def __init__(self):
        self.repository = RoleRepository()
        self.app_repository = ApplicationRepository()
    
    def get_role(self, db: Session, role_id: int) -> Optional[Role]:
        """Get single role without relationships"""
        db_role = self.repository.get(db, role_id)
        return Role.model_validate(db_role) if db_role else None
    
    def get_role_with_details(self, db: Session, role_id: int) -> Optional[RoleWithDetails]:
        """Get role with application info and assigned users"""
        db_role = self.repository.get_with_application_and_users(db, role_id)
        if not db_role:
            return None
        
        # Extract application info
        application_info = ApplicationInfo.model_validate(db_role.application)
        
        # Extract users from user_roles relationship
        users = [User.model_validate(ur.user) for ur in db_role.user_roles]
        
        # Create role with details
        role_data = Role.model_validate(db_role).model_dump()
        role_data['application'] = application_info
        role_data['users'] = users
        
        return RoleWithDetails.model_validate(role_data)
    
    def get_roles(
        self, 
        db: Session, 
        app_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Role]:
        """Get list of roles, optionally filtered by application"""
        if app_id:
            db_roles = self.repository.get_by_app_id(db, app_id, skip=skip, limit=limit)
        else:
            db_roles = self.repository.get_multi(db, skip=skip, limit=limit)
        
        return [Role.model_validate(role) for role in db_roles]
    
    def create_role(self, db: Session, role: RoleCreate) -> Optional[Role]:
        """Create new role"""
        # Verify application exists
        app = self.app_repository.get(db, role.r_app_id)
        if app is None:  # Explicit None check
            return None
        
        # Check if role code already exists for this application
        existing_role = self.repository.get_by_app_and_code(db, role.r_app_id, role.r_code)
        if existing_role is not None:  # Explicit None check
            return None
        
        db_role = self.repository.create(db, role.model_dump())
        return Role.model_validate(db_role) if db_role else None
    
    def update_role(
        self, 
        db: Session, 
        role_id: int, 
        role: RoleUpdate
    ) -> Optional[Role]:
        """Update existing role"""
        db_role = self.repository.get(db, role_id)
        if db_role is None:  # Explicit None check
            return None
        
        update_data = role.model_dump(exclude_unset=True)
        
        # If updating role code, check for conflicts
        if "r_code" in update_data:
            # Cast to int to fix the type error
            existing_role = self.repository.get_by_app_and_code(
                db, cast(int, db_role.r_app_id), update_data["r_code"]
            )
            if existing_role is not None and cast(int, existing_role.r_id) != role_id:  # Cast to int
                return None
        
        updated_role = self.repository.update(db, db_role, update_data)
        return Role.model_validate(updated_role) if updated_role else None
    
    def delete_role(self, db: Session, role_id: int) -> bool:
        """Delete role"""
        deleted = self.repository.delete(db, role_id)
        return deleted is not None
    
    def get_total_roles(self, db: Session, app_id: Optional[int] = None) -> int:
        """Get total count of roles"""
        if app_id:
            return self.repository.count_by_app_id(db, app_id)
        return self.repository.count(db)
    
    def update_role_permissions(
        self, 
        db: Session, 
        role_id: int, 
        permissions: Dict[str, Any]
    ) -> Optional[Role]:
        """Update permissions for a specific role"""
        db_role = self.repository.get(db, role_id)
        if db_role is None:  # Explicit None check
            return None
        
        update_data = {"r_permissions": permissions}
        updated_role = self.repository.update(db, db_role, update_data)
        return Role.model_validate(updated_role) if updated_role else None