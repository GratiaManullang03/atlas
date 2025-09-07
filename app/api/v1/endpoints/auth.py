from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth import AuthService
from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest, 
    RefreshTokenResponse, LogoutRequest, UserInfo,
    ForgotPasswordRequest, ResetPasswordRequest, RequestEmailVerificationRequest
)
from app.schemas.common import ResponseBase, DataResponse
from app.api.deps import require_auth
from app.core.security import verify_token

router = APIRouter()
auth_service = AuthService()

@router.post("/login", response_model=DataResponse[LoginResponse])
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user with username/email and password"""
    user = auth_service.authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or inactive account"
        )
    
    tokens = auth_service.create_tokens(db, user)
    
    return DataResponse(
        success=True,
        message="Login successful",
        data=tokens
    )

@router.post("/refresh", response_model=DataResponse[RefreshTokenResponse])
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    # 1. Verifikasi dan dekode refresh token untuk mendapatkan payload
    payload = verify_token(refresh_data.refresh_token)
    
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = int(payload["sub"])

    # 2. Panggil service dengan user_id
    new_token = auth_service.refresh_access_token(
        db, 
        refresh_token=refresh_data.refresh_token, 
        user_id=user_id
    )
    
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return DataResponse(
        success=True,
        message="Token refreshed successfully",
        data=new_token
    )

@router.post("/logout", response_model=ResponseBase)
def logout(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db)
):
    """Logout user by invalidating refresh token"""
    # 1. Decode the token to get the user_id
    payload = verify_token(logout_data.refresh_token)
    
    if not payload or not payload.get("sub"):
        # Even if the token is invalid, we can return a success-like response
        # to prevent leaking information about token validity.
        return ResponseBase(success=True, message="Logout successful")

    user_id = int(payload["sub"])

    # 2. Call the logout service with the user_id
    success = auth_service.logout_user(
        db, 
        refresh_token=logout_data.refresh_token, 
        user_id=user_id
    )
    
    return ResponseBase(
        success=success,
        message="Logout successful" if success else "Token not found"
    )

@router.get("/me", response_model=DataResponse[UserInfo])
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """Get current user information"""
    user_info = auth_service.get_user_info(db, int(current_user["user_id"]))
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return DataResponse(
        success=True,
        message="User info retrieved successfully",
        data=user_info
    )

@router.post("/request-verification", response_model=ResponseBase)
async def request_verification_email(
    request: RequestEmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Request a new email verification link.
    """
    await auth_service.request_email_verification(db, request.email)
    
    return ResponseBase(
        success=True, 
        message="Jika email terdaftar, email verifikasi akan dikirim."
    )

@router.post("/verify-email", response_model=ResponseBase)
def verify_user_email(
    token: str, # Menerima token sebagai query parameter atau body
    db: Session = Depends(get_db)
):
    """
    Verify user's email with a token.
    """
    success = auth_service.verify_email(db, token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token verifikasi tidak valid atau sudah kedaluwarsa."
        )
    return ResponseBase(success=True, message="Email berhasil diverifikasi.")

@router.post("/forgot-password", response_model=ResponseBase)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset link.
    """
    # Jalankan langsung di foreground untuk debugging
    await auth_service.forgot_password(db, request.email)
    
    return ResponseBase(
        success=True,
        message="Jika email terdaftar, tautan reset password akan dikirim."
    )

@router.post("/reset-password", response_model=ResponseBase)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset user's password with a token.
    """
    success = auth_service.reset_password(db, request.token, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token reset tidak valid atau sudah kedaluwarsa."
        )
    return ResponseBase(success=True, message="Password berhasil direset.")