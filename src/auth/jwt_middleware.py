"""
AX-001: JWT Middleware for Arcade.XYZ
Replaces x-user-id header with proper JWT auth.
7-day access tokens + 30-day refresh tokens with revocation support.
"""

import jwt
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple, Set
from functools import wraps
import os

logger = logging.getLogger(__name__)


class JWTConfig:
    """JWT configuration."""
    
    ACCESS_TOKEN_EXPIRY = 7 * 24 * 3600  # 7 days in seconds
    REFRESH_TOKEN_EXPIRY = 30 * 24 * 3600  # 30 days in seconds
    ALGORITHM = "HS256"
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize JWT config.
        
        Args:
            secret_key: JWT signing secret (defaults to env var JWT_SECRET)
        """
        self.secret_key = secret_key or os.getenv('JWT_SECRET', 'change-me-in-production')
        if self.secret_key == 'change-me-in-production':
            logger.warning("Using default JWT secret - set JWT_SECRET env var in production")


class TokenRevocationStore:
    """In-memory token revocation cache with Redis-ready interface."""
    
    def __init__(self, cleanup_interval: int = 3600):
        """
        Initialize revocation store.
        
        Args:
            cleanup_interval: Run cleanup every N seconds
        """
        self.revoked_tokens: Set[str] = set()
        self.revocation_timestamps: Dict[str, float] = {}
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = datetime.now(timezone.utc).timestamp()
    
    def revoke(self, token_jti: str, expiry_timestamp: float) -> None:
        """
        Revoke a token by JTI.
        
        Args:
            token_jti: JWT ID (jti claim)
            expiry_timestamp: Token expiry time (for cleanup)
        """
        self.revoked_tokens.add(token_jti)
        self.revocation_timestamps[token_jti] = expiry_timestamp
        logger.info(f"Token revoked: {token_jti[:16]}...")
    
    def is_revoked(self, token_jti: str) -> bool:
        """Check if token has been revoked."""
        return token_jti in self.revoked_tokens
    
    def cleanup_expired(self) -> int:
        """Remove tokens past expiry. Returns count removed."""
        now = datetime.now(timezone.utc).timestamp()
        expired = [
            jti for jti, exp_ts in self.revocation_timestamps.items()
            if exp_ts < now
        ]
        for jti in expired:
            self.revoked_tokens.discard(jti)
            del self.revocation_timestamps[jti]
        
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired revocations")
        return len(expired)


class JWTHandler:
    """JWT token generation and validation."""
    
    def __init__(self, config: JWTConfig):
        """
        Initialize JWT handler.
        
        Args:
            config: JWTConfig instance
        """
        self.config = config
        self.revocation_store = TokenRevocationStore()
    
    def generate_token_pair(
        self,
        user_id: str,
        user_email: Optional[str] = None,
        scopes: Optional[list] = None
    ) -> Dict[str, str]:
        """
        Generate access and refresh token pair.
        
        Args:
            user_id: User ID (UUID)
            user_email: User email (optional)
            scopes: List of permission scopes (optional)
        
        Returns:
            {
                "access_token": "...",
                "refresh_token": "...",
                "token_type": "Bearer",
                "expires_in": 604800,
                "refresh_expires_in": 2592000
            }
        """
        now = datetime.now(timezone.utc)
        
        # Generate JWT ID (for revocation tracking)
        token_jti = hashlib.sha256(
            f"{user_id}{now.isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Access token (7 days)
        access_payload = {
            "sub": user_id,
            "email": user_email,
            "type": "access",
            "jti": token_jti,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.config.ACCESS_TOKEN_EXPIRY)).timestamp()),
            "scopes": scopes or ["read", "write"]
        }
        
        access_token = jwt.encode(
            access_payload,
            self.config.secret_key,
            algorithm=self.config.ALGORITHM
        )
        
        # Refresh token (30 days)
        refresh_jti = hashlib.sha256(
            f"{user_id}{now.isoformat()}refresh".encode()
        ).hexdigest()[:16]
        
        refresh_payload = {
            "sub": user_id,
            "type": "refresh",
            "jti": refresh_jti,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.config.REFRESH_TOKEN_EXPIRY)).timestamp())
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            self.config.secret_key,
            algorithm=self.config.ALGORITHM
        )
        
        logger.info(f"Token pair generated for user {user_id}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.config.ACCESS_TOKEN_EXPIRY,
            "refresh_expires_in": self.config.REFRESH_TOKEN_EXPIRY
        }
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string (without "Bearer " prefix)
        
        Returns:
            (is_valid, decoded_payload, error_message)
        """
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.ALGORITHM]
            )
            
            # Check revocation
            if self.revocation_store.is_revoked(payload.get("jti")):
                return False, None, "Token has been revoked"
            
            logger.debug(f"Token verified for user {payload.get('sub')}")
            return True, payload, None
            
        except jwt.ExpiredSignatureError:
            return False, None, "Token has expired"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid token: {str(e)}"
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return False, None, "Token verification failed"
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Issue new access token using refresh token.
        
        Args:
            refresh_token: Refresh token string
        
        Returns:
            (success, {new access_token, expires_in}, error_message)
        """
        is_valid, payload, error = self.verify_token(refresh_token)
        
        if not is_valid:
            return False, None, error
        
        if payload.get("type") != "refresh":
            return False, None, "Not a refresh token"
        
        # Generate new access token
        user_id = payload.get("sub")
        now = datetime.now(timezone.utc)
        
        access_jti = hashlib.sha256(
            f"{user_id}{now.isoformat()}access".encode()
        ).hexdigest()[:16]
        
        access_payload = {
            "sub": user_id,
            "type": "access",
            "jti": access_jti,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.config.ACCESS_TOKEN_EXPIRY)).timestamp()),
            "scopes": payload.get("scopes", ["read", "write"])
        }
        
        new_access_token = jwt.encode(
            access_payload,
            self.config.secret_key,
            algorithm=self.config.ALGORITHM
        )
        
        logger.info(f"Access token refreshed for user {user_id}")
        
        return True, {
            "access_token": new_access_token,
            "expires_in": self.config.ACCESS_TOKEN_EXPIRY
        }, None
    
    def revoke_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Revoke a token (add to revocation list).
        
        Args:
            token: JWT token to revoke
        
        Returns:
            (success, error_message)
        """
        is_valid, payload, error = self.verify_token(token)
        
        if not is_valid:
            return False, error
        
        exp_ts = payload.get("exp")
        self.revocation_store.revoke(payload.get("jti"), exp_ts)
        
        return True, None


# FastAPI/Flask middleware helpers
def extract_token_from_header(auth_header: Optional[str]) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        auth_header: Value of Authorization header
    
    Returns:
        Token string or None
    """
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


def require_auth(jwt_handler: JWTHandler):
    """
    Decorator for protecting endpoints.
    Usage:
        @require_auth(jwt_handler)
        def get_profile(request, user_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")
            token = extract_token_from_header(auth_header)
            
            if not token:
                return {"error": "Missing Authorization header"}, 401
            
            is_valid, payload, error = jwt_handler.verify_token(token)
            if not is_valid:
                return {"error": error}, 401
            
            # Attach user_id to request
            request.user_id = payload.get("sub")
            request.user_payload = payload
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator
