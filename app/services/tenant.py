from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import create_tenant_schema


class TenantService:
    def __init__(self):
        pass
    
    def create_tenant(self, db: Session, schema_name: str) -> bool:
        """Create a new tenant schema with all required tables"""
        try:
            # Validate schema name (basic validation)
            if not schema_name.isalnum() and '_' not in schema_name:
                return False
            
            # Create schema using stored procedure
            create_tenant_schema(db, schema_name)
            return True
            
        except Exception as e:
            print(f"Error creating tenant schema: {e}")
            return False
    
    def list_tenant_schemas(self, db: Session) -> List[str]:
        """List all tenant schemas (excluding system schemas)"""
        query = text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'public')
            ORDER BY schema_name
        """)
        
        result = db.execute(query)
        return [row[0] for row in result.fetchall()]
    
    def schema_exists(self, db: Session, schema_name: str) -> bool:
        """Check if a schema exists"""
        query = text("""
            SELECT 1 FROM information_schema.schemata 
            WHERE schema_name = :schema_name
        """)
        
        result = db.execute(query, {"schema_name": schema_name})
        return result.fetchone() is not None
    
    def delete_tenant(self, db: Session, schema_name: str) -> bool:
        """Delete a tenant schema (use with caution!)"""
        try:
            if schema_name in ['public', 'information_schema', 'pg_catalog']:
                return False
            
            db.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting tenant schema: {e}")
            return False