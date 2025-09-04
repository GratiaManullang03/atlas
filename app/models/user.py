from sqlalchemy import (
    Column, BigInteger, String, Boolean, DateTime, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    u_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    u_username = Column(String(100), unique=True, nullable=False, index=True)
    u_email = Column(String(255), unique=True, nullable=False, index=True)
    u_password_hash = Column(String(255), nullable=False)
    u_full_name = Column(String(255))
    u_status = Column(
        String(20), 
        default="active",
        nullable=False
    )
    u_email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            u_status.in_(["active", "inactive", "pending_verification"]),
            name="check_user_status"
        ),
    )