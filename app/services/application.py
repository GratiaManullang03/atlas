from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.application import ApplicationRepository
from app.schemas.application import Application, ApplicationCreate, ApplicationUpdate


class ApplicationService:
    def __init__(self):
        self.repository = ApplicationRepository()
    
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