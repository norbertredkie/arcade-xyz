"""
AX-003: Input Validation Schemas for Arcade.XYZ
20+ API endpoints validation with XSS/SQL injection prevention.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


# XSS/Injection Prevention
def sanitize_text(value: str, max_length: int = 255) -> str:
    """Remove XSS vectors and limit length."""
    if not isinstance(value, str):
        return str(value)
    
    # Remove HTML tags
    value = re.sub(r'<[^>]*>', '', value)
    
    # Remove XSS patterns
    xss_patterns = [
        r'javascript:',
        r'on\w+\s*=',
        r'<script',
        r'</script>',
        r'<iframe',
        r'eval\(',
        r'expression\(',
    ]
    for pattern in xss_patterns:
        value = re.sub(pattern, '', value, flags=re.IGNORECASE)
    
    return value.strip()[:max_length]


def validate_sql_injection(value: str) -> bool:
    """Detect SQL injection patterns."""
    sql_patterns = [
        r"('\s*(or|and)\s*'|--|;|\*|xp_|sp_)",
        r'union\s+select',
        r'drop\s+(table|database)',
        r'exec\(',
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, value, flags=re.IGNORECASE):
            return True
    
    return False


# Game Management Schemas
class GameCreateSchema(BaseModel):
    """Game creation validation."""
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=5000)
    genre: Literal['puzzle', 'action', 'strategy', 'arcade', 'casual', 'other']
    difficulty: Literal['easy', 'medium', 'hard', 'extreme']
    multiplayer: bool = False
    max_players: Optional[int] = Field(default=1, ge=1, le=100)
    price_usd: Optional[float] = Field(default=0, ge=0, le=999.99)
    thumbnail_url: Optional[str] = None
    
    @field_validator('title', 'description')
    @classmethod
    def sanitize_text_fields(cls, value: str) -> str:
        if validate_sql_injection(value):
            raise ValueError('Potential SQL injection detected')
        return sanitize_text(value, max_length=5000)
    
    @field_validator('thumbnail_url')
    @classmethod
    def validate_url(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        if not value.startswith('https://'):
            raise ValueError('Thumbnail must be HTTPS')
        if len(value) > 2048:
            raise ValueError('URL too long')
        return value
    
    @model_validator(mode='after')
    def validate_multiplayer_settings(self):
        if self.multiplayer and self.max_players and self.max_players < 2:
            raise ValueError('Multiplayer games must support 2+ players')
        return self


class GameUpdateSchema(BaseModel):
    """Game update validation."""
    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, min_length=10, max_length=5000)
    difficulty: Optional[Literal['easy', 'medium', 'hard', 'extreme']] = None
    price_usd: Optional[float] = Field(default=None, ge=0, le=999.99)
    active: Optional[bool] = None
    
    @field_validator('title', 'description')
    @classmethod
    def sanitize_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if validate_sql_injection(value):
            raise ValueError('Potential SQL injection detected')
        return sanitize_text(value)


# User Management Schemas
class UserCreateSchema(BaseModel):
    """User registration validation."""
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=12)
    avatar_url: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValueError('Invalid characters in username')
        return value
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain uppercase')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain lowercase')
        if not re.search(r'[0-9]', value):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*]', value):
            raise ValueError('Password must contain special character')
        return value
    
    @field_validator('avatar_url')
    @classmethod
    def validate_avatar_url(cls, value: Optional[str]) -> Optional[str]:
        if value and not value.startswith('https://'):
            raise ValueError('Avatar URL must be HTTPS')
        return value


class UserUpdateSchema(BaseModel):
    """User profile update validation."""
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    bio: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = None
    
    @field_validator('username', 'bio')
    @classmethod
    def sanitize_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return sanitize_text(value, max_length=500)


# Payment Schemas
class PaymentSchema(BaseModel):
    """Payment/purchase validation."""
    game_id: str = Field(..., min_length=36, max_length=36)  # UUID
    user_id: str = Field(..., min_length=36, max_length=36)  # UUID
    amount_usd: float = Field(..., ge=0.01, le=10000)
    payment_method: Literal['card', 'paypal', 'google_play', 'app_store']
    payment_token: str = Field(..., min_length=10, max_length=1024)
    idempotency_key: Optional[str] = None
    
    @field_validator('game_id', 'user_id')
    @classmethod
    def validate_uuid_format(cls, value: str) -> str:
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', value, re.I):
            raise ValueError('Invalid UUID format')
        return value
    
    @field_validator('idempotency_key')
    @classmethod
    def validate_idempotency_key(cls, value: Optional[str]) -> Optional[str]:
        if value and not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValueError('Invalid idempotency key format')
        return value


class RefundSchema(BaseModel):
    """Refund request validation."""
    payment_id: str = Field(..., min_length=36)
    reason: Literal['user_requested', 'game_issue', 'duplicate', 'other']
    notes: Optional[str] = Field(default=None, max_length=1000)
    
    @field_validator('notes')
    @classmethod
    def sanitize_notes(cls, value: Optional[str]) -> Optional[str]:
        if value:
            if validate_sql_injection(value):
                raise ValueError('Invalid characters in notes')
            return sanitize_text(value, max_length=1000)
        return None


# Gameplay Schemas
class GameSessionStartSchema(BaseModel):
    """Start game session validation."""
    game_id: str = Field(..., min_length=36, max_length=36)
    user_id: str = Field(..., min_length=36, max_length=36)
    difficulty_override: Optional[Literal['easy', 'medium', 'hard', 'extreme']] = None
    
    @field_validator('game_id', 'user_id')
    @classmethod
    def validate_uuid(cls, value: str) -> str:
        if not re.match(r'^[0-9a-f-]{36}$', value, re.I):
            raise ValueError('Invalid UUID')
        return value


class GameActionSchema(BaseModel):
    """In-game action validation."""
    session_id: str = Field(..., min_length=36, max_length=36)
    action: str = Field(..., min_length=1, max_length=100)
    payload: Optional[Dict[str, Any]] = None
    timestamp: int = Field(..., ge=0)
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, value: str) -> str:
        if not re.match(r'^[a-z_]+$', value):
            raise ValueError('Action must be lowercase with underscores')
        return value
    
    @field_validator('payload', mode='before')
    @classmethod
    def validate_payload(cls, value: Optional[Dict]) -> Optional[Dict]:
        if value is None:
            return None
        # Limit payload size
        if len(str(value)) > 10000:
            raise ValueError('Payload too large')
        return value


# AI/Content Schemas
class AIChatSchema(BaseModel):
    """AI chat/content generation validation."""
    game_id: str = Field(..., min_length=36, max_length=36)
    user_id: str = Field(..., min_length=36, max_length=36)
    message: str = Field(..., min_length=1, max_length=2000)
    context: Optional[str] = Field(default=None, max_length=5000)
    
    @field_validator('message', 'context')
    @classmethod
    def sanitize_message(cls, value: str) -> str:
        if validate_sql_injection(value):
            raise ValueError('Potential SQL injection in message')
        return sanitize_text(value, max_length=2000)


# Reporting/Moderation Schemas
class ReportSchema(BaseModel):
    """Report inappropriate content validation."""
    reported_user_id: str = Field(..., min_length=36, max_length=36)
    report_type: Literal['abuse', 'cheating', 'inappropriate_content', 'spam', 'other']
    description: str = Field(..., min_length=10, max_length=2000)
    evidence_urls: Optional[List[str]] = None
    
    @field_validator('description')
    @classmethod
    def sanitize_description(cls, value: str) -> str:
        if validate_sql_injection(value):
            raise ValueError('Invalid characters in description')
        return sanitize_text(value, max_length=2000)
    
    @field_validator('evidence_urls')
    @classmethod
    def validate_urls(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value:
            for url in value:
                if not url.startswith('https://'):
                    raise ValueError('URLs must be HTTPS')
                if len(url) > 2048:
                    raise ValueError('URL too long')
            return value
        return None


# Schema registry
SCHEMAS = {
    'game_create': GameCreateSchema,
    'game_update': GameUpdateSchema,
    'user_create': UserCreateSchema,
    'user_update': UserUpdateSchema,
    'payment': PaymentSchema,
    'refund': RefundSchema,
    'game_session_start': GameSessionStartSchema,
    'game_action': GameActionSchema,
    'ai_chat': AIChatSchema,
    'report': ReportSchema,
}


def validate_schema(schema_name: str, data: dict) -> tuple[bool, Optional[dict], Optional[str]]:
    """
    Validate data against schema.
    
    Returns:
        (is_valid, validated_data, error_message)
    """
    if schema_name not in SCHEMAS:
        return False, None, f"Unknown schema: {schema_name}"
    
    try:
        schema = SCHEMAS[schema_name]
        validated = schema(**data)
        return True, validated.model_dump(), None
    except Exception as e:
        logger.warning(f"Validation error ({schema_name}): {str(e)}")
        return False, None, str(e)
