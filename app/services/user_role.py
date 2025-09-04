from typing import List, Optional, Set
from sqlalchemy.orm import Session

from app.repositories.user_role import UserRoleRepository
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.schemas.user_role import UserRole, UserRoleWithDetails

class UserRoleService:
    def __init__(self):
        self.repository = UserRoleRepository()
        self.user_repository = UserRepository()
        self.role_repository = RoleRepository()
    
    def assign_role_to_user(self, db: Session, user_id: int, role_id: int) -> Optional[UserRole]:
        """Assign role to user"""
        # Verify user exists
        user = self.user_repository.get(db, user_id)
        if not user:
            return None
        
        # Verify role exists
        role = self.role_repository.get(db, role_id)
        if not role:
            return None
        
        # Check if assignment already exists
        existing = self.repository.get_by_user_and_role(db, user_id, role_id)
        if existing:
            return UserRole.model_validate(existing)
        
        # Create assignment
        assignment_data = {
            "ur_user_id": user_id,
            "ur_role_id": role_id
        }
        
        db_assignment = self.repository.create(db, assignment_data)
        return UserRole.model_validate(db_assignment)
    
    def assign_roles_to_user(self, db: Session, user_id: int, role_ids: List[int]) -> List[UserRole]:
        """Assign multiple roles to user"""
        results = []
        for role_id in role_ids:
            assignment = self.assign_role_to_user(db, user_id, role_id)
            if assignment:
                results.append(assignment)
        return results
    
    def remove_role_from_user(self, db: Session, user_id: int, role_id: int) -> bool:
        """Remove role from user"""
        return self.repository.delete_by_user_and_role(db, user_id, role_id)
    
    def get_user_roles(self, db: Session, user_id: int) -> List[UserRoleWithDetails]:
        """Get all roles assigned to a user with details"""
        roles_data = self.repository.get_user_roles_with_details(db, user_id)
        
        return [
            UserRoleWithDetails(
                ur_id=role_data["ur_id"],
                role_id=role_data["role_id"],
                role_code=role_data["role_code"],
                role_name=role_data["role_name"],
                role_level=role_data["role_level"],
                app_id=role_data["app_id"],
                app_name=role_data["app_name"],
                app_code=role_data["app_code"],
                created_at=role_data["created_at"]
            ) for role_data in roles_data
        ]
    
    def get_user_permissions(self, db: Session, user_id: int) -> Set[str]:
        """
        Get a consolidated set of permissions for a user from all their roles.
        Permissions are in the format 'resource:action', e.g., 'users:read'.
        """
        user_roles = self.repository.get_user_roles_with_permissions(db, user_id)
        
        permissions: Set[str] = set()
        
        for role in user_roles:
            permissions_data = getattr(role, "r_permissions", None)
            
            if permissions_data is None:
                continue
            
            # Cek untuk izin super admin ("all": true)
            if role.r_permissions.get("all") is True:
                permissions.add("*")
                # Jika sudah super admin, tidak perlu proses lebih lanjut
                return permissions

            # Proses izin granular
            for resource, actions in role.r_permissions.items():
                if isinstance(actions, list):
                    for action in actions:
                        permissions.add(f"{resource}:{action}")
        
        return permissions
