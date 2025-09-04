import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, cast
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    verify_password, create_access_token, get_password_hash,
    create_short_lived_token, verify_short_lived_token, pwd_context
)
from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.schemas.auth import LoginResponse, RefreshTokenResponse, UserInfo
from app.schemas.user import User
from app.core.mailer import send_email
from app.services.user_role import UserRoleService 

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.refresh_token_repo = RefreshTokenRepository()
        self.user_role_service = UserRoleService()
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        db_user = self.user_repo.get_by_username_or_email(db, username)
        
        if not db_user:
            return None
        
        if not verify_password(password, cast(str, db_user.u_password_hash)):
            return None
        
        if cast(str, db_user.u_status) != "active":
            return None
        
        return User.model_validate(db_user)
    
    def create_tokens(self, db: Session, user: User, user_agent: str = "", ip_address: str = "") -> LoginResponse:
        """Create tokens with enhanced security"""
        # Gunakan bcrypt untuk hash refresh token
        refresh_token = secrets.token_urlsafe(64)
        refresh_token_hash = pwd_context.hash(refresh_token)
        
        # Simpan dengan expiration
        refresh_token_data = {
            "rt_user_id": user.u_id,
            "rt_token_hash": refresh_token_hash,
            "rt_expires_at": datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        }
        
        self.refresh_token_repo.create(db, refresh_token_data)
        
        # Buat access token dengan fingerprint
        access_token_data = {
            "sub": str(user.u_id),
            "username": user.u_username,
            "email": user.u_email,
            "status": user.u_status
        }
        access_token = create_access_token(access_token_data, user_agent, ip_address)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> Optional[RefreshTokenResponse]:
        """Create new access token from refresh token"""
        # Hash the provided refresh token
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # Find refresh token in database
        db_refresh_token = self.refresh_token_repo.get_by_token_hash(db, token_hash)
        
        if not db_refresh_token:
            return None
        
        # Get user
        user = self.user_repo.get(db, db_refresh_token.rt_user_id)
        
        if not user or cast(str, user.u_status) != "active":
            return None
        
        # Create new access token
        access_token_data = {
            "sub": str(user.u_id),
            "username": cast(str, user.u_username),
            "email": cast(str, user.u_email),
            "status": cast(str, user.u_status)
        }
        access_token = create_access_token(access_token_data)
        
        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def logout_user(self, db: Session, refresh_token: str) -> bool:
        """Logout user by removing refresh token"""
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        return self.refresh_token_repo.delete_by_token_hash(db, token_hash)
    
    def get_user_info(self, db: Session, user_id: int) -> Optional[UserInfo]:
        """Get user info by ID"""
        user = self.user_repo.get(db, user_id)
        
        if not user:
            return None
        
        # Get user roles
        user_roles = self.user_role_service.get_user_roles(db, user_id)
        
        return UserInfo(
            u_id=cast(int, user.u_id),
            u_username=cast(str, user.u_username),
            u_email=cast(str, user.u_email),
            u_full_name=cast(Optional[str], user.u_full_name),
            u_status=cast(str, user.u_status),
            u_email_verified=cast(bool, user.u_email_verified),
            roles=user_roles # Menambahkan roles ke dalam response
        )
    
    async def request_email_verification(self, db: Session, email: str):
        """
        Memproses permintaan untuk mengirim email verifikasi.
        """
        user = self.user_repo.get_by_email(db, email)
        if not user:
            # Tidak melempar error untuk mencegah user enumeration
            return
        
        if cast(bool, user.u_email_verified):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email sudah terverifikasi.")

        # Buat token verifikasi (berlaku 1 jam)
        token_data = {"sub": cast(str, user.u_email), "scope": "email_verification"}
        verification_token = create_short_lived_token(token_data, timedelta(hours=1))
        
        # Kirim email
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        await send_email(
            subject="Verifikasi Email Anda",
            recipient=cast(str, user.u_email),
            template_name="verify_email.html",
            template_body={"verification_link": verification_link}
        )

    def verify_email(self, db: Session, token: str) -> bool:
        """
        Memverifikasi email pengguna berdasarkan token.
        """
        payload = verify_short_lived_token(token)
        if not payload or payload.get("scope") != "email_verification":
            return False # Token tidak valid atau scope salah
        
        email = payload.get("sub")
        # Add this check to ensure email is a string
        if not email or not isinstance(email, str):
            return False
            
        user = self.user_repo.get_by_email(db, email)
        if not user or cast(bool, user.u_email_verified):
            return False
            
        # Update status verifikasi
        user.u_email_verified = True  # type: ignore
        db.add(user)
        db.commit()
        
        return True

    async def forgot_password(self, db: Session, email: str):
        """
        Memproses permintaan lupa password dan mengirim email reset.
        """
        user = self.user_repo.get_by_email(db, email)
        if not user:
            # Tidak melempar error untuk mencegah user enumeration
            return

        # Buat token reset password (berlaku 15 menit)
        token_data = {"sub": cast(str, user.u_email), "scope": "password_reset"}
        reset_token = create_short_lived_token(token_data, timedelta(minutes=15))
        
        # Kirim email
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        await send_email(
            subject="Permintaan Reset Password",
            recipient=cast(str, user.u_email),
            template_name="reset_password.html",
            template_body={"reset_link": reset_link}
        )

    def reset_password(self, db: Session, token: str, new_password: str) -> bool:
        """
        Mereset password pengguna dengan token yang valid.
        """
        payload = verify_short_lived_token(token)
        if not payload or payload.get("scope") != "password_reset":
            return False

        email = payload.get("sub")
        # Add this check to ensure email is a string
        if not email or not isinstance(email, str):
            return False
            
        user = self.user_repo.get_by_email(db, email)
        if not user:
            return False
            
        # Hash dan update password baru
        user.u_password_hash = get_password_hash(new_password)  # type: ignore
        db.add(user)
        db.commit()

        return True