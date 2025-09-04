from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.u_username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.u_email == email).first()
    
    def get_by_username_or_email(self, db: Session, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        return db.query(User).filter(
            (User.u_username == identifier) | (User.u_email == identifier)
        ).first()