from typing import Optional, List, cast
from sqlalchemy.orm import Session

from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, User
from app.core.security import get_password_hash
from app.models.user import User as UserModel  # Import the SQLAlchemy model


class UserService:
    def __init__(self):
        self.repository = UserRepository()
    
    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get single user"""
        db_user = self.repository.get(db, user_id)
        return User.model_validate(db_user) if db_user else None
    
    def get_users(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Get list of users"""
        db_users = self.repository.get_multi(db, skip=skip, limit=limit)
        return [User.model_validate(user) for user in db_users]
    
    def create_user(self, db: Session, user: UserCreate) -> Optional[User]:
        """Create new user"""
        # Check if username already exists
        existing_user = self.repository.get_by_username(db, user.u_username)
        if existing_user is not None:  # Explicit None check
            return None
        
        # Check if email already exists
        existing_email = self.repository.get_by_email(db, user.u_email)
        if existing_email is not None:  # Explicit None check
            return None
        
        # Hash password
        user_data = user.model_dump()
        user_data["u_password_hash"] = get_password_hash(user_data.pop("u_password"))
        
        db_user = self.repository.create(db, user_data)
        return User.model_validate(db_user) if db_user else None
    
    def update_user(
        self, 
        db: Session, 
        user_id: int, 
        user: UserUpdate
    ) -> Optional[User]:
        """Update existing user"""
        db_user = self.repository.get(db, user_id)
        if db_user is None:  # Explicit None check
            return None
        
        update_data = user.model_dump(exclude_unset=True)
        
        # Check for username conflicts
        if "u_username" in update_data:
            existing_user = self.repository.get_by_username(db, update_data["u_username"])
            if existing_user is not None and cast(int, existing_user.u_id) != user_id:
                return None
        
        # Check for email conflicts
        if "u_email" in update_data:
            existing_email = self.repository.get_by_email(db, update_data["u_email"])
            if existing_email is not None and cast(int, existing_email.u_id) != user_id:
                return None
        
        # Hash password if provided
        if "u_password" in update_data:
            update_data["u_password_hash"] = get_password_hash(update_data.pop("u_password"))
        
        updated_user = self.repository.update(db, db_user, update_data)
        return User.model_validate(updated_user) if updated_user else None
    
    def delete_user(self, db: Session, user_id: int) -> bool:
        """Delete user"""
        deleted = self.repository.delete(db, user_id)
        return deleted is not None
    
    def get_total_users(self, db: Session) -> int:
        """Get total count of users"""
        return self.repository.count(db)
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        db_user = self.repository.get_by_username(db, username)
        return User.model_validate(db_user) if db_user else None
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        db_user = self.repository.get_by_email(db, email)
        return User.model_validate(db_user) if db_user else None