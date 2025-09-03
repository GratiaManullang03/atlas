from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    rt_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    rt_user_id = Column(Integer, ForeignKey("users.u_id", ondelete="CASCADE"), nullable=False)
    rt_token_hash = Column(String(255), nullable=False, index=True)
    rt_expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)