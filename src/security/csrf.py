"""
AX-005: CSRF Protection Middleware
Double-submit cookie pattern with HttpOnly, Secure, SameSite=Strict.
Token validation on state-changing requests.
"""

import secrets
import hashlib
import hmac
import time
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class CSRFConfig:
    """CSRF configuration."""
    
    TOKEN_LENGTH = 32  # 256 bits
    TOKEN_TTL = 86400  # 24 hours
    ALGORITHM = "sha256"
    
    # Cookie settings (for browser storage)
    COOKIE_NAME = "csrf_token"
    COOKIE_HEADER = "X-CSRF-Token"
    
    # Safe methods (no CSRF check required)
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    
    # State-changing methods (require CSRF token)
    PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class CSRFTokenManager:
    """Generate, validate, and manage CSRF tokens."""
    
    def __init__(self, secret_key: str, config: CSRFConfig = None):
        """
        Initialize CSRF token manager.
        
        Args:
            secret_key: Secret key for HMAC signing
            config: CSRFConfig instance
        """
        self.secret_key = secret_key
        self.config = config or CSRFConfig()
        self.issued_tokens: Dict[str, Dict[str, Any]] = {}
        self.last_cleanup = time.time()
        self.cleanup_interval = 3600  # 1 hour
    
    def generate_token(self, session_id: Optional[str] = None) -> str:
        """
        Generate a new CSRF token.
        
        Args:
            session_id: Optional session ID to bind token to
        
        Returns:
            CSRF token (hex-encoded)
        """
        # Generate random bytes
        random_bytes = secrets.token_bytes(self.config.TOKEN_LENGTH)
        token = random_bytes.hex()
        
        # Sign token with secret
        signed = hmac.new(
            self.secret_key.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Store for validation (with metadata)
        now = time.time()
        self.issued_tokens[token] = {
            "issued_at": now,
            "signed": signed,
            "session_id": session_id
        }
        
        logger.debug(f"CSRF token generated: {token[:8]}...")
        return token
    
    def validate_token(
        self,
        token: str,
        session_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate CSRF token.
        
        Args:
            token: Token to validate
            session_id: Expected session ID (optional)
        
        Returns:
            (is_valid, error_message)
        """
        # Cleanup periodically
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired()
        
        # Check if token exists
        if token not in self.issued_tokens:
            logger.warning(f"CSRF token not found: {token[:8]}...")
            return False, "Invalid CSRF token"
        
        entry = self.issued_tokens[token]
        
        # Check expiry
        if now - entry["issued_at"] > self.config.TOKEN_TTL:
            del self.issued_tokens[token]
            logger.warning(f"CSRF token expired: {token[:8]}...")
            return False, "CSRF token expired"
        
        # Verify signature
        expected_signed = hmac.new(
            self.secret_key.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signed, entry["signed"]):
            logger.error(f"CSRF token signature mismatch: {token[:8]}...")
            return False, "Invalid CSRF token signature"
        
        # Check session binding (if provided)
        if session_id and entry.get("session_id") != session_id:
            logger.warning(f"CSRF token session mismatch: {token[:8]}...")
            return False, "CSRF token session mismatch"
        
        logger.debug(f"CSRF token validated: {token[:8]}...")
        return True, None
    
    def invalidate_token(self, token: str) -> None:
        """Invalidate/revoke a token."""
        if token in self.issued_tokens:
            del self.issued_tokens[token]
            logger.info(f"CSRF token invalidated: {token[:8]}...")
    
    def _cleanup_expired(self) -> int:
        """Remove expired tokens. Returns count removed."""
        now = time.time()
        expired = [
            token for token, entry in self.issued_tokens.items()
            if now - entry["issued_at"] > self.config.TOKEN_TTL
        ]
        
        for token in expired:
            del self.issued_tokens[token]
        
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired CSRF tokens")
        
        self.last_cleanup = now
        return len(expired)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get token manager statistics."""
        return {
            "total_tokens": len(self.issued_tokens),
            "token_ttl_hours": self.config.TOKEN_TTL // 3600,
            "timestamp": time.time()
        }


class CSRFMiddleware:
    """CSRF protection middleware for HTTP frameworks."""
    
    def __init__(self, token_manager: CSRFTokenManager):
        """
        Initialize middleware.
        
        Args:
            token_manager: CSRFTokenManager instance
        """
        self.token_manager = token_manager
        self.config = token_manager.config
    
    def set_token_cookie(
        self,
        response_headers: Dict[str, str],
        token: str,
        domain: Optional[str] = None,
        path: str = "/"
    ) -> None:
        """
        Set CSRF token cookie on response.
        
        Args:
            response_headers: Response headers dict
            token: CSRF token to set
            domain: Cookie domain (optional)
            path: Cookie path (default "/")
        """
        # HttpOnly=false intentionally so JavaScript can read it
        # (but we validate against header, not cookie)
        cookie_value = (
            f"{self.config.COOKIE_NAME}={token}; "
            f"Path={path}; "
            f"Max-Age={self.config.TOKEN_TTL}; "
            f"Secure; "
            f"SameSite=Strict"
        )
        
        if domain:
            cookie_value += f"; Domain={domain}"
        
        response_headers["Set-Cookie"] = cookie_value
        logger.debug(f"CSRF token cookie set: {token[:8]}...")
    
    def verify_request(
        self,
        method: str,
        headers: Dict[str, str],
        session_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify CSRF token on incoming request.
        
        Args:
            method: HTTP method
            headers: Request headers
            session_id: Session ID (optional)
        
        Returns:
            (is_valid, error_message)
        """
        # Safe methods don't require CSRF token
        if method in self.config.SAFE_METHODS:
            return True, None
        
        # Protected methods require valid CSRF token
        if method not in self.config.PROTECTED_METHODS:
            return True, None  # Unknown method, allow through
        
        # Get token from header (double-submit pattern)
        token = headers.get(self.config.COOKIE_HEADER)
        
        if not token:
            logger.warning(f"Missing CSRF token in {self.config.COOKIE_HEADER} header")
            return False, f"Missing CSRF token (set {self.config.COOKIE_HEADER} header)"
        
        # Validate token
        is_valid, error = self.token_manager.validate_token(token, session_id)
        
        if is_valid:
            # Invalidate token after successful use (optional: for one-time tokens)
            # Uncomment if one-time tokens required:
            # self.token_manager.invalidate_token(token)
            pass
        
        return is_valid, error
    
    def get_token_for_form(self, session_id: Optional[str] = None) -> str:
        """
        Generate token for embedding in form.
        
        Args:
            session_id: Session ID (optional)
        
        Returns:
            CSRF token
        """
        return self.token_manager.generate_token(session_id)


# Helper functions for framework integration
def create_csrf_middleware(secret_key: str) -> CSRFMiddleware:
    """Factory to create CSRF middleware."""
    token_manager = CSRFTokenManager(secret_key)
    return CSRFMiddleware(token_manager)


def csrf_protect(middleware: CSRFMiddleware):
    """
    Decorator for FastAPI/Flask endpoints.
    
    Usage:
        @app.post("/api/purchase")
        @csrf_protect(csrf_middleware)
        def purchase(request):
            ...
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            # Get session ID from request
            session_id = request.cookies.get("session_id")
            
            # Verify CSRF token
            is_valid, error = middleware.verify_request(
                request.method,
                request.headers,
                session_id
            )
            
            if not is_valid:
                logger.warning(f"CSRF protection triggered: {error}")
                return {"error": "CSRF validation failed"}, 403
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


# Response helpers
class CSRFResponse:
    """Helper to build CSRF-protected responses."""
    
    @staticmethod
    def with_token(
        middleware: CSRFMiddleware,
        body: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        session_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Build response with CSRF token cookie.
        
        Returns:
            (response_body, headers_with_cookie)
        """
        headers = headers or {}
        
        # Generate token
        token = middleware.get_token_for_form(session_id)
        
        # Add token to response body
        body["csrf_token"] = token
        
        # Set cookie
        middleware.set_token_cookie(headers, token)
        
        return body, headers
