from typing import Optional
from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self):
        super().__init__(Application)
    
    def get_by_code(self, db: Session, app_code: str) -> Optional[Application]:
        """Get application by code"""
        return db.query(Application).filter(Application.app_code == app_code).first()
