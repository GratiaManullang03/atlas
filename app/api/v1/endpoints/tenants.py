from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.tenant import TenantService
from app.schemas.tenant import TenantCreate, TenantInfo, TenantList
from app.schemas.common import DataResponse, ResponseBase
from app.utils.database_init import seed_new_tenant_data

router = APIRouter()
tenant_service = TenantService()


@router.post("/", response_model=DataResponse[TenantInfo])
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db)
):
    """Create a new tenant schema"""
    # Validate schema name
    if not tenant.schema_name.replace('_', '').isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schema name must contain only alphanumeric characters and underscores"
        )
    
    if len(tenant.schema_name) > 63:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schema name must be 63 characters or less"
        )
    
    # Check if schema already exists
    if tenant_service.schema_exists(db, tenant.schema_name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Schema already exists"
        )
    
    # Create tenant schema
    success = tenant_service.create_tenant(db, tenant.schema_name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tenant schema"
        )
    
    seed_new_tenant_data(db, tenant.schema_name)
    
    tenant_info = TenantInfo(
        schema_name=tenant.schema_name,
        table_count=5,  # We create 5 tables per tenant
        created=True
    )
    
    return DataResponse(
        success=True,
        message="Tenant created successfully",
        data=tenant_info
    )


@router.get("/", response_model=DataResponse[TenantList])
def list_tenants(
    db: Session = Depends(get_db)
):
    """List all tenant schemas"""
    schemas = tenant_service.list_tenant_schemas(db)
    
    tenant_list = TenantList(
        schemas=schemas,
        count=len(schemas)
    )
    
    return DataResponse(
        success=True,
        message="Tenants retrieved successfully",
        data=tenant_list
    )


@router.get("/{schema_name}", response_model=DataResponse[TenantInfo])
def get_tenant(
    schema_name: str,
    db: Session = Depends(get_db)
):
    """Get tenant information"""
    if not tenant_service.schema_exists(db, schema_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant schema not found"
        )
    
    tenant_info = TenantInfo(
        schema_name=schema_name,
        table_count=5,
        created=True
    )
    
    return DataResponse(
        success=True,
        message="Tenant information retrieved successfully",
        data=tenant_info
    )


@router.delete("/{schema_name}", response_model=ResponseBase)
def delete_tenant(
    schema_name: str,
    db: Session = Depends(get_db)
):
    """Delete a tenant schema (use with extreme caution!)"""
    if not tenant_service.schema_exists(db, schema_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant schema not found"
        )
    
    success = tenant_service.delete_tenant(db, schema_name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tenant schema"
        )
    
    return ResponseBase(
        success=True,
        message="Tenant deleted successfully"
    )