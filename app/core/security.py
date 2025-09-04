import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import hmac

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenSecurity:
    """Enhanced token security with additional validations"""
    
    @staticmethod
    def generate_secure_token(length: int = 64) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_hex(length)
    
    @staticmethod
    def create_token_with_fingerprint(user_id: str, user_agent: str, ip: str) -> Dict[str, str]:
        """Create token with browser/IP fingerprint for added security"""
        fingerprint = hashlib.sha256(f"{user_agent}:{ip}:{user_id}".encode()).hexdigest()[:16]
        return {"fingerprint": fingerprint}
    
    @staticmethod
    def verify_token_fingerprint(token_fingerprint: str, user_agent: str, ip: str, user_id: str) -> bool:
        """Verify token fingerprint matches current session"""
        expected_fingerprint = hashlib.sha256(f"{user_agent}:{ip}:{user_id}".encode()).hexdigest()[:16]
        return hmac.compare_digest(token_fingerprint, expected_fingerprint)

class Security:
    """Security utilities"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], user_agent: str = "", ip_address: str = "") -> str:
        """Create JWT access token with session fingerprint"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add session fingerprint
        if user_agent and ip_address:
            session_fingerprint = hashlib.sha256(f"{user_agent}{ip_address}".encode()).hexdigest()
            to_encode["fingerprint"] = session_fingerprint
        
        to_encode.update({
            "exp": expire, 
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "jti": secrets.token_hex(16)
        })
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token with enhanced security"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({
            "exp": expire, 
            "type": "refresh",
            "iat": datetime.now(timezone.utc),
            "jti": TokenSecurity.generate_secure_token(16)
        })
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, expected_type: str = "") -> Optional[Dict[str, Any]]:
        """Enhanced token verification with type checking"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Check if token is expired
            if datetime.now(timezone.utc) > datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc):
                return None
            
            # Check token type if specified
            if expected_type and payload.get("type") != expected_type:
                return None
                
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def hash_token_for_storage(token: str) -> str:
        """Hash token for secure database storage"""
        return hashlib.sha256(token.encode()).hexdigest()

# Update existing functions
def create_access_token(data: Dict[str, Any], user_agent: str = "", ip_address: str = "") -> str:
    """Create JWT access token - backward compatibility"""
    return Security.create_access_token(data, user_agent, ip_address)

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token - backward compatibility"""
    return Security.create_refresh_token(data)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token - backward compatibility"""
    return Security.verify_token(token)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_short_lived_token(data: Dict[str, Any], expires_delta: timedelta) -> str:
    """Create token JWT with custom expiration"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": TokenSecurity.generate_secure_token(8)
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_short_lived_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify short-lived JWT token"""
    return Security.verify_token(token)