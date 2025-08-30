from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

class UserLogin(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v

class UserRegister(BaseModel):
    email: str
    password: str
    organization_name: Optional[str] = None  # Optional org name for new registrations
    
    @validator('email')
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v

# Enhanced organization and user context models
class OrganizationInfo(BaseModel):
    id: str
    name: str
    slug: str
    role: str  # User's role in this organization
    permissions: List[str] = []
    settings: Dict[str, Any] = {}

class UserContext(BaseModel):
    """Enhanced user context with client isolation support"""
    id: str
    email: str
    created_at: datetime
    # Primary organization (for backward compatibility)
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    # All organizations user belongs to
    organizations: List[OrganizationInfo] = []
    # Global permissions
    global_permissions: List[str] = []
    # Security metadata
    last_login: Optional[datetime] = None
    login_count: Optional[int] = 0

class UserResponse(BaseModel):
    """Basic user response (legacy compatibility)"""
    id: str
    email: str
    created_at: datetime

class EnhancedUserResponse(BaseModel):
    """Enhanced user response with client context"""
    id: str
    email: str
    created_at: datetime
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    organizations: List[OrganizationInfo] = []
    permissions: List[str] = []

class TokenPayload(BaseModel):
    """JWT token payload with client context"""
    sub: str  # user_id
    email: str
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    role: Optional[str] = None
    permissions: List[str] = []
    organizations: List[str] = []  # List of organization IDs
    exp: int
    iat: int
    token_version: str = "v2"  # Version for migration tracking

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    # Enhanced fields (optional for backward compatibility)
    expires_in: Optional[int] = 3600
    token_version: Optional[str] = "v1"

class EnhancedTokenResponse(BaseModel):
    """Enhanced token response with full client context"""
    access_token: str
    token_type: str = "bearer"
    user: EnhancedUserResponse
    expires_in: int = 3600
    token_version: str = "v2"
    client_context: Dict[str, Any] = {}

class UserInDB(BaseModel):
    id: str
    email: str
    created_at: Optional[datetime] = None
    # Enhanced fields for client context
    client_id: Optional[str] = None
    organizations: List[OrganizationInfo] = []
    permissions: List[str] = []

# Security event logging models
class SecurityEvent(BaseModel):
    event_type: str  # login_attempt, login_success, login_failure, token_validation, etc.
    user_id: Optional[str] = None
    email: Optional[str] = None
    client_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    details: Dict[str, Any] = {}
    timestamp: datetime = datetime.utcnow()

# Token validation models
class TokenValidationRequest(BaseModel):
    token: str
    require_client_context: bool = True
    validate_permissions: List[str] = []

class TokenValidationResponse(BaseModel):
    valid: bool
    user_context: Optional[UserContext] = None
    error: Optional[str] = None
    token_version: Optional[str] = None
    expires_at: Optional[datetime] = None