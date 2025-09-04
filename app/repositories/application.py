from typing import Optional
from sqlalchemy.orm import Session, selectinload

from app.models.application import Application
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.base import BaseRepository

class ApplicationRepository(BaseRepository[Application]):
    def __init__(self):
        super().__init__(Application)
    
    def get_by_code(self, db: Session, app_code: str) -> Optional[Application]:
        """Get application by code"""
        return db.query(Application).filter(Application.app_code == app_code).first()

    def get_application_with_roles_and_users(self, db: Session, app_id: int) -> Optional[Application]:
        """Get application with roles and users"""
        return (
            db.query(Application)
            .options(
                selectinload(Application.roles)
                .selectinload(Role.user_roles)
                .selectinload(UserRole.user)
            )
            .filter(Application.app_id == app_id)
            .first()
        )