from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository

class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self):
        super().__init__(RefreshToken)
    
    def get_by_token_hash(self, db: Session, token_hash: str) -> Optional[RefreshToken]:
        """Get refresh token by hash"""
        return db.query(RefreshToken).filter(
            RefreshToken.rt_token_hash == token_hash,
            RefreshToken.rt_expires_at > datetime.now()
        ).first()
    
    def get_by_user_id(self, db: Session, user_id: int) -> List[RefreshToken]:
        """Get all active refresh tokens for a user"""
        return db.query(RefreshToken).filter(
            RefreshToken.rt_user_id == user_id,
            RefreshToken.rt_expires_at > datetime.now()
        ).all()
    
    def delete_expired(self, db: Session) -> int:
        """Delete all expired refresh tokens"""
        expired_tokens = db.query(RefreshToken).filter(
            RefreshToken.rt_expires_at <= datetime.now()
        )
        count = expired_tokens.count()
        expired_tokens.delete()
        db.commit()
        return count
    
    def delete_by_token_hash(self, db: Session, token_hash: str) -> bool:
        """Delete refresh token by hash"""
        token = db.query(RefreshToken).filter(
            RefreshToken.rt_token_hash == token_hash
        ).first()
        
        if token:
            db.delete(token)
            db.commit()
            return True
        return False
    
    def delete_by_user_id(self, db: Session, user_id: int) -> int:
        """Delete all refresh tokens for a user"""
        tokens = db.query(RefreshToken).filter(RefreshToken.rt_user_id == user_id)
        count = tokens.count()
        tokens.delete()
        db.commit()
        return count