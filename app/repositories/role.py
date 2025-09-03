from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self):
        super().__init__(Role)
    
    def get_by_app_and_code(self, db: Session, app_id: int, role_code: str) -> Optional[Role]:
        """Get role by application ID and role code"""
        return db.query(Role).filter(
            Role.r_app_id == app_id,
            Role.r_code == role_code
        ).first()
    
    def get_by_app_id(self, db: Session, app_id: int, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get roles by application ID"""
        return db.query(Role).filter(
            Role.r_app_id == app_id
        ).offset(skip).limit(limit).all()
    
    def count_by_app_id(self, db: Session, app_id: int) -> int:
        """Count roles by application ID"""
        return db.query(Role).filter(Role.r_app_id == app_id).count()