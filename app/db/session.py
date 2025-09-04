from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings
from fastapi import Header
from typing import Optional

# Normalisasi URL database (postgres:// -> postgresql+asyncpg://)
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    # db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

# if "?sslmode" in db_url:
#     db_url = db_url.split("?sslmode")[0] 

engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.DEBUG
    # connect_args={
    #     # Gunakan 'true' jika Anda ingin koneksi SSL tanpa verifikasi sertifikat (tidak disarankan untuk produksi)
    #     # Atau gunakan objek ssl.Context untuk konfigurasi SSL yang lebih aman
    #     "ssl": "require" # atau 'true' tergantung kebutuhan
    # }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db(
    tenant_schema: Optional[str] = Header(None, alias="X-Tenant-Schema")
) -> Generator[Session, None, None]:
    """Dependency to get database session with tenant schema context"""
    db = SessionLocal()
    try:
        schema_to_set = tenant_schema or settings.DEFAULT_SCHEMA
        set_schema_search_path(db, schema_to_set)
        yield db
    finally:
        db.close()

def set_schema_search_path(db: Session, schema_name: str):
    """Set schema search path for multi-tenant support"""
    db.execute(text(f"SET search_path TO {schema_name}, public"))
    db.commit()


def create_tenant_schema(db: Session, schema_name: str):
    """Create tenant schema using the stored procedure"""
    db.execute(text("SELECT create_tenant_schema(:schema_name)"), {"schema_name": schema_name})
    db.commit()