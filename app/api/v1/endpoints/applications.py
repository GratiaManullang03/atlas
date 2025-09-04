from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.application import ApplicationService
from app.schemas.application import (
    Application,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationWithRoles,
)
from app.schemas.common import DataResponse, PaginationResponse

router = APIRouter()
application_service = ApplicationService()

@router.get("/", response_model=PaginationResponse[Application])
def get_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    # current_user: dict = Depends(require_auth)  # Uncomment untuk require auth
):
    """Get list of applications with pagination"""
    applications = application_service.get_applications(db, skip=skip, limit=limit)
    total = application_service.get_total_applications(db)
    
    return PaginationResponse(
        success=True,
        message="Applications retrieved successfully",
        data=applications,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{app_id}", response_model=DataResponse[ApplicationWithRoles])
def get_application(
    app_id: int,
    db: Session = Depends(get_db)
):
    """Get single application by ID with roles and users"""
    application = application_service.get_application_details(db, app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return DataResponse(
        success=True,
        message="Application retrieved successfully",
        data=application
    )

@router.post("/", response_model=DataResponse[Application])
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create new application"""
    # Check if app_code already exists
    existing_app = application_service.get_by_code(db, application.app_code)
    if existing_app:
        raise HTTPException(
            status_code=400, 
            detail="Application with this code already exists"
        )
    
    new_app = application_service.create_application(db, application)
    
    return DataResponse(
        success=True,
        message="Application created successfully",
        data=new_app
    )

@router.put("/{app_id}", response_model=DataResponse[Application])
def update_application(
    app_id: int,
    application: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update existing application"""
    # If updating app_code, check for conflicts
    if application.app_code:
        existing_app = application_service.get_by_code(db, application.app_code)
        if existing_app and existing_app.app_id != app_id:
            raise HTTPException(
                status_code=400,
                detail="Application with this code already exists"
            )
    
    updated_app = application_service.update_application(db, app_id, application)
    if not updated_app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return DataResponse(
        success=True,
        message="Application updated successfully",
        data=updated_app
    )

@router.delete("/{app_id}", response_model=DataResponse[None])
def delete_application(
    app_id: int,
    db: Session = Depends(get_db)
):
    """Delete application"""
    deleted = application_service.delete_application(db, app_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return DataResponse(
        success=True,
        message="Application deleted successfully",
        data=None
    )