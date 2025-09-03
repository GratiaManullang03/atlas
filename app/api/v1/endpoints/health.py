from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import redis

from app.db.session import get_db
from app.api.deps import get_redis
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/", response_model=ResponseBase)
async def health_check(
    db: Session = Depends(get_db),
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """Health check endpoint"""
    # Check database
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy ({e})"

    
    # Check Redis (if configured)
    redis_status = "not configured"
    if redis_client:
        try:
            redis_client.ping()
            redis_status = "healthy"
        except Exception:
            redis_status = "unhealthy"
    
    return ResponseBase(
        success=True,
        message=f"Database: {db_status}, Redis: {redis_status}"
    )