from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    ur_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    ur_user_id = Column(Integer, ForeignKey("users.u_id", ondelete="CASCADE"), nullable=False)
    ur_role_id = Column(Integer, ForeignKey("roles.r_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("ur_user_id", "ur_role_id", name="uq_user_role"),
    )