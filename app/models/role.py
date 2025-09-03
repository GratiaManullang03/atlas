from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"

    r_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    r_app_id = Column(Integer, ForeignKey("applications.app_id", ondelete="CASCADE"), nullable=False)
    r_code = Column(String(100), nullable=False)
    r_name = Column(String(255), nullable=False)
    r_level = Column(Integer, default=0, nullable=False)
    r_permissions = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("r_app_id", "r_code", name="uq_role_app_code"),
    )