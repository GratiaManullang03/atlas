from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.application import ApplicationRepository
from app.repositories.role import RoleRepository
from app.schemas.application import (
    Application,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationWithRoles,
    RoleWithUsers,
)
from app.schemas.user import User

class ApplicationService:
    def __init__(self):
        self.repository = ApplicationRepository()
        self.role_repository = RoleRepository()

    def get_application_details(self, db: Session, app_id: int) -> Optional[ApplicationWithRoles]:
        """Get application details with roles and users"""
        db_app = self.repository.get_application_with_roles_and_users(db, app_id)
        if not db_app:
            return None

        roles_with_users = []
        for role in db_app.roles:
            users_in_role = [User.model_validate(user_role.user) for user_role in role.user_roles]
            roles_with_users.append(
                RoleWithUsers(
                    r_id=role.r_id,
                    r_code=role.r_code,
                    r_name=role.r_name,
                    users=users_in_role,
                )
            )

        app_data = Application.model_validate(db_app).model_dump()
        app_data["roles"] = roles_with_users

        return ApplicationWithRoles.model_validate(app_data)
    
    def get_application(self, db: Session, app_id: int) -> Optional[Application]:
        """Get single application"""
        db_app = self.repository.get(db, app_id)
        return Application.model_validate(db_app) if db_app else None

    def get_applications(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Application]:
        """Get list of applications"""
        db_apps = self.repository.get_multi(db, skip=skip, limit=limit)
        return [Application.model_validate(app) for app in db_apps]

    def create_application(self, db: Session, app: ApplicationCreate) -> Application:
        """Create new application"""
        db_app = self.repository.create(db, app.model_dump())
        return Application.model_validate(db_app)

    def update_application(
        self,
        db: Session,
        app_id: int,
        app: ApplicationUpdate
    ) -> Optional[Application]:
        """Update existing application"""
        db_app = self.repository.get(db, app_id)
        if not db_app:
            return None

        update_data = app.model_dump(exclude_unset=True)
        db_app = self.repository.update(db, db_app, update_data)
        return Application.model_validate(db_app)

    def delete_application(self, db: Session, app_id: int) -> bool:
        """Delete application"""
        deleted = self.repository.delete(db, app_id)
        return deleted is not None

    def get_total_applications(self, db: Session) -> int:
        """Get total count of applications"""
        return self.repository.count(db)

    def get_by_code(self, db: Session, app_code: str) -> Optional[Application]:
        """Get application by code"""
        db_app = self.repository.get_by_code(db, app_code)
        return Application.model_validate(db_app) if db_app else None