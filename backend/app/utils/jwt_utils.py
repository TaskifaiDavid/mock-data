"""
JWT utilities for secure token management with client context.
Eliminates the need for service role token validation.
"""

import jwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.utils.config import get_settings
from app.models.auth import TokenPayload, UserContext, OrganizationInfo


class JWTManager:
    """Secure JWT token management without service role dependency"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.algorithm = self.settings.jwt_algorithm
        self.secret_key = self.settings.jwt_secret_key
        self.expiration_minutes = self.settings.jwt_expiration_minutes
    
    def create_access_token(
        self, 
        user_id: str, 
        email: str,
        client_id: Optional[str] = None,
        client_name: Optional[str] = None,
        role: Optional[str] = None,
        permissions: list = None,
        organizations: list = None,
        extra_claims: Dict[str, Any] = None
    ) -> str:
        """
        Create a JWT access token with client context.
        This eliminates the need for service role token validation.
        """
        try:
            now = datetime.now(timezone.utc)
            expire = now + timedelta(minutes=self.expiration_minutes)
            
            # Base payload with client context
            payload = {
                "sub": user_id,
                "email": email,
                "client_id": client_id,
                "client_name": client_name,
                "role": role or "member",
                "permissions": permissions or [],
                "organizations": organizations or [],
                "iat": int(now.timestamp()),
                "exp": int(expire.timestamp()),
                "token_version": "v2",  # Version for migration tracking
                "iss": "mockrepo-auth",  # Token issuer
                "aud": "mockrepo-api"    # Token audience
            }
            
            # Add any extra claims
            if extra_claims:
                payload.update(extra_claims)
            
            # Create and return token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
            self.logger.info(f"Created v2 token for user {email} with client_id {client_id}")
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create access token: {str(e)}")
            raise
    
    def create_legacy_token(self, user_id: str, email: str) -> str:
        """
        Create a legacy v1 token for backward compatibility.
        """
        try:
            now = datetime.now(timezone.utc)
            expire = now + timedelta(minutes=self.expiration_minutes)
            
            payload = {
                "sub": user_id,
                "email": email,
                "iat": int(now.timestamp()),
                "exp": int(expire.timestamp()),
                "token_version": "v1",
                "iss": "mockrepo-auth",
                "aud": "mockrepo-api"
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            self.logger.info(f"Created v1 compatibility token for user {email}")
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create legacy token: {str(e)}")
            raise
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate and decode JWT token without requiring service role.
        Returns token payload if valid, None if invalid.
        """
        try:
            # Debug: Log token info before validation
            unsafe_payload = self.decode_token_unsafe(token)
            if unsafe_payload:
                exp_time = unsafe_payload.get("exp", 0)
                current_time = int(datetime.utcnow().timestamp())
                
                # Ensure exp_time is an integer for comparison
                if isinstance(exp_time, str):
                    try:
                        exp_time = int(float(exp_time))
                    except (ValueError, TypeError):
                        self.logger.warning(f"🔍 TOKEN DEBUG - Invalid exp format: {exp_time}, type: {type(exp_time)}")
                        exp_time = 0
                
                self.logger.info(f"🔍 TOKEN DEBUG - exp: {exp_time}, current: {current_time}, diff: {exp_time - current_time} seconds")
                self.logger.info(f"🔍 TOKEN CONTENT - iss: {unsafe_payload.get('iss')}, aud: {unsafe_payload.get('aud')}, version: {unsafe_payload.get('token_version')}")
            
            # Decode and validate token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience="mockrepo-api",
                issuer="mockrepo-auth"
            )
            
            # JWT library already validates expiration, no need for manual check
            
            self.logger.debug(f"Token validated for user {payload.get('email')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("🔍 JWT ERROR: Token expired (ExpiredSignatureError)")
            return None
        except jwt.InvalidAudienceError as e:
            self.logger.warning(f"🔍 JWT ERROR: Invalid audience - {str(e)}")
            return None
        except jwt.InvalidIssuerError as e:
            self.logger.warning(f"🔍 JWT ERROR: Invalid issuer - {str(e)}")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"🔍 JWT ERROR: Invalid token - {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"🔍 JWT ERROR: Unexpected error - {str(e)}")
            return None
    
    def decode_token_unsafe(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without validation (for debugging/migration).
        WARNING: Only use for debugging or migration purposes.
        """
        try:
            # Decode without verification for debugging
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            self.logger.error(f"Failed to decode token: {str(e)}")
            return None
    
    def extract_user_context(self, payload: Dict[str, Any]) -> UserContext:
        """
        Extract user context from validated token payload.
        Handles both v1 and v2 token formats for backward compatibility.
        """
        try:
            token_version = payload.get("token_version", "v1")
            
            if token_version == "v2":
                # Enhanced v2 token with full client context
                organizations = []
                if payload.get("organizations"):
                    # Note: In v2 tokens, organizations are stored as IDs
                    # Full organization details would be fetched separately if needed
                    for org_id in payload.get("organizations", []):
                        organizations.append(OrganizationInfo(
                            id=org_id,
                            name=payload.get("client_name", "Unknown"),  # Fallback
                            slug="unknown",
                            role=payload.get("role", "member"),
                            permissions=payload.get("permissions", [])
                        ))
                
                return UserContext(
                    id=payload["sub"],
                    email=payload["email"],
                    created_at=datetime.now(timezone.utc),  # Would be fetched from DB in real implementation
                    client_id=payload.get("client_id"),
                    client_name=payload.get("client_name"),
                    organizations=organizations,
                    global_permissions=payload.get("permissions", []),
                    login_count=payload.get("login_count", 0)
                )
            else:
                # Legacy v1 token - minimal context
                return UserContext(
                    id=payload["sub"],
                    email=payload["email"],
                    created_at=datetime.now(timezone.utc),
                    organizations=[],
                    global_permissions=[]
                )
                
        except Exception as e:
            self.logger.error(f"Failed to extract user context: {str(e)}")
            raise
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired without full validation"""
        try:
            payload = self.decode_token_unsafe(token)
            if not payload:
                return True
            
            exp = payload.get("exp", 0)
            return datetime.now(timezone.utc).timestamp() > exp
            
        except Exception:
            return True
    
    def get_token_version(self, token: str) -> str:
        """Get token version for migration tracking"""
        try:
            payload = self.decode_token_unsafe(token)
            return payload.get("token_version", "v1") if payload else "unknown"
        except Exception:
            return "unknown"


# Global JWT manager instance
jwt_manager = JWTManager()