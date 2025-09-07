from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)  # type: ignore

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get single record by ID"""
        pk_column = list(self.model.__table__.primary_key.columns)[0]
        return db.query(self.model).filter(pk_column == id).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: Dict[str, Any]) -> ModelType:
        """Create new record"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_multi(self, db: Session, objs_in: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple new records in a single transaction."""
        # Create model instances from the input dictionaries
        db_objs = [self.model(**obj_in) for obj_in in objs_in]
        
        # Use bulk_save_objects for efficient insertion
        db.bulk_save_objects(db_objs, return_defaults=True)
        db.commit()
        return db_objs
    
    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """Update existing record"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: Any) -> Optional[ModelType]:
        """Delete record"""
        pk_column = list(self.model.__table__.primary_key.columns)[0]
        obj = db.query(self.model).filter(pk_column == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def count(self, db: Session) -> int:
        """Count total records"""
        pk_column = list(self.model.__table__.primary_key.columns)[0]
        return db.query(func.count(pk_column)).scalar() or 0
    
    def execute_raw_sql(
        self, db: Session, query: str, params: Optional[Dict[str, Any]] = None
    ):
        """Execute raw SQL for complex queries"""
        result = db.execute(text(query), params or {})
        return result.fetchall()
