from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.user_role import UserRole
from app.models.role import Role
from app.repositories.base import BaseRepository


class UserRoleRepository(BaseRepository[UserRole]):
    def __init__(self):
        super().__init__(UserRole)
    
    def get_by_user_id(self, db: Session, user_id: int) -> List[UserRole]:
        """Get all roles assigned to a user"""
        return db.query(UserRole).filter(UserRole.ur_user_id == user_id).all()
    
    def get_by_user_and_role(self, db: Session, user_id: int, role_id: int) -> Optional[UserRole]:
        """Get specific user-role assignment"""
        return db.query(UserRole).filter(
            UserRole.ur_user_id == user_id,
            UserRole.ur_role_id == role_id
        ).first()
    
    def delete_by_user_and_role(self, db: Session, user_id: int, role_id: int) -> bool:
        """Delete specific user-role assignment"""
        user_role = self.get_by_user_and_role(db, user_id, role_id)
        if user_role:
            db.delete(user_role)
            db.commit()
            return True
        return False
    
    def get_user_roles_with_details(self, db: Session, user_id: int) -> List[dict]:
        """Get user roles with application and role details"""
        query = text("""
            SELECT 
                ur.ur_id,
                r.r_id as role_id,
                r.r_code as role_code,
                r.r_name as role_name,
                r.r_level as role_level,
                a.app_id,
                a.app_name,
                a.app_code,
                ur.created_at
            FROM user_roles ur
            JOIN roles r ON ur.ur_role_id = r.r_id
            JOIN applications a ON r.r_app_id = a.app_id
            WHERE ur.ur_user_id = :user_id
            ORDER BY a.app_name, r.r_level DESC, r.r_name
        """)
        
        result = db.execute(query, {"user_id": user_id})
        return [dict(row._mapping) for row in result.fetchall()]
    
    def get_user_roles_with_permissions(self, db: Session, user_id: int) -> List[Role]:
        """Get all role objects for a user to access their permissions"""
        return db.query(Role).join(UserRole, Role.r_id == UserRole.ur_role_id).filter(UserRole.ur_user_id == user_id).all()