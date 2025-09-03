from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    app_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    app_code = Column(String(50), unique=True, nullable=False, index=True)
    app_name = Column(String(255), nullable=False)
    app_description = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())