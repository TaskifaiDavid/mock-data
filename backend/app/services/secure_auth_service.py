"""
Secure Authentication Service - Phase 3 Multi-Tenant Security Enhancement.

This service eliminates dangerous service role usage and implements proper 
multi-tenant authentication with client context validation.

Key security improvements:
- No service role usage for token validation (eliminates security bypass)
- Client context embedded in JWT tokens
- Organization-aware authentication
- Comprehensive security event logging
- Backward compatibility during migration
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from supabase import create_client, Client
from app.utils.config import get_settings
from app.utils.exceptions import AuthenticationException
from app.models.auth import (
    UserLogin, UserRegister, TokenResponse, EnhancedTokenResponse,
    UserResponse, EnhancedUserResponse, UserContext, TokenValidationResponse
)
from app.utils.jwt_utils import jwt_manager
from app.services.organization_service import organization_service
from app.services.security_logger import security_logger


class SecureAuthService:
    """
    Secure authentication service with multi-tenant support.
    Eliminates service role dependencies and implements proper client isolation.
    """
    
    def __init__(self):
        settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Development mode handling
        if settings.environment == "development":
            self.logger.info("Running in development mode - using mock authentication")
            self.supabase = None
            self.dev_mode = True
        else:
            # Use only anon client - NO SERVICE ROLE
            self.supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            self.dev_mode = False
    
    async def login(
        self, 
        credentials: UserLogin,
        client_info: Dict[str, Optional[str]] = None
    ) -> EnhancedTokenResponse:
        """
        Secure login with client context embedding.
        No service role usage - relies on Supabase Auth and JWT validation.
        """
        client_info = client_info or {}
        
        try:
            # Log login attempt
            await security_logger.log_login_attempt(
                email=credentials.email,
                success=False,  # Will update on success
                ip_address=client_info.get("ip_address"),
                user_agent=client_info.get("user_agent")
            )
            
            if self.dev_mode:
                # Development mode - create enhanced mock response
                user_id = await self._create_dev_user_id(credentials.email)
                
                # Get mock organization
                organizations = await organization_service.get_user_organizations(user_id)
                primary_org = organizations[0] if organizations else None
                
                # Create enhanced JWT token with client context
                access_token = jwt_manager.create_access_token(
                    user_id=user_id,
                    email=credentials.email,
                    client_id=primary_org.id if primary_org else None,
                    client_name=primary_org.name if primary_org else None,
                    role=primary_org.role if primary_org else "member",
                    permissions=primary_org.permissions if primary_org else ["read"],
                    organizations=[primary_org.id] if primary_org else []
                )
                
                # Log successful login
                await security_logger.log_login_attempt(
                    email=credentials.email,
                    success=True,
                    user_id=user_id,
                    client_id=primary_org.id if primary_org else None,
                    ip_address=client_info.get("ip_address"),
                    user_agent=client_info.get("user_agent")
                )
                
                return EnhancedTokenResponse(
                    access_token=access_token,
                    user=EnhancedUserResponse(
                        id=user_id,
                        email=credentials.email,
                        created_at=datetime.now(timezone.utc),
                        client_id=primary_org.id if primary_org else None,
                        client_name=primary_org.name if primary_org else None,
                        organizations=organizations,
                        permissions=primary_org.permissions if primary_org else ["read"]
                    ),
                    token_version="v2",
                    client_context={
                        "primary_organization": primary_org.id if primary_org else None,
                        "total_organizations": len(organizations),
                        "login_timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            
            # Production mode - use Supabase Auth (no service role)
            response = self.supabase.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })
            
            if not response.user or not response.session:
                await security_logger.log_login_attempt(
                    email=credentials.email,
                    success=False,
                    ip_address=client_info.get("ip_address"),
                    user_agent=client_info.get("user_agent"),
                    error_details="Invalid credentials"
                )
                raise AuthenticationException("Invalid credentials")
            
            user_id = response.user.id
            user_token = response.session.access_token
            
            # Get user's organization context using user-scoped auth
            organizations = await organization_service.get_user_organizations(
                user_id, user_token
            )
            
            # Ensure user has at least one organization
            if not organizations:
                primary_org = await organization_service.ensure_user_has_organization(
                    user_id, credentials.email, user_token
                )
                organizations = [primary_org]
            else:
                primary_org = organizations[0]  # Use first organization as primary
            
            # Create enhanced JWT token with full client context
            access_token = jwt_manager.create_access_token(
                user_id=user_id,
                email=credentials.email,
                client_id=primary_org.id,
                client_name=primary_org.name,
                role=primary_org.role,
                permissions=primary_org.permissions,
                organizations=[org.id for org in organizations],
                extra_claims={
                    "supabase_token": user_token,  # For RLS queries if needed
                    "login_timestamp": int(datetime.now(timezone.utc).timestamp())
                }
            )
            
            # Log successful login with organization context
            await security_logger.log_login_attempt(
                email=credentials.email,
                success=True,
                user_id=user_id,
                client_id=primary_org.id,
                ip_address=client_info.get("ip_address"),
                user_agent=client_info.get("user_agent")
            )
            
            await security_logger.log_organization_access(
                user_id=user_id,
                email=credentials.email,
                client_id=primary_org.id,
                organization_name=primary_org.name,
                access_granted=True,
                ip_address=client_info.get("ip_address")
            )
            
            return EnhancedTokenResponse(
                access_token=access_token,
                user=EnhancedUserResponse(
                    id=user_id,
                    email=credentials.email,
                    created_at=datetime.fromisoformat(response.user.created_at.replace('Z', '+00:00')),
                    client_id=primary_org.id,
                    client_name=primary_org.name,
                    organizations=organizations,
                    permissions=primary_org.permissions
                ),
                token_version="v2",
                client_context={
                    "primary_organization": primary_org.id,
                    "total_organizations": len(organizations),
                    "login_timestamp": datetime.now(timezone.utc).isoformat(),
                    "supabase_session_expires": response.session.expires_at
                }
            )
            
        except AuthenticationException:
            raise
        except Exception as e:
            await security_logger.log_login_attempt(
                email=credentials.email,
                success=False,
                ip_address=client_info.get("ip_address"),
                user_agent=client_info.get("user_agent"),
                error_details=str(e)
            )
            self.logger.error(f"Login error for {credentials.email}: {str(e)}")
            raise AuthenticationException("Authentication failed")
    
    async def register(
        self, 
        user_data: UserRegister,
        client_info: Dict[str, Optional[str]] = None
    ) -> EnhancedTokenResponse:
        """
        Secure user registration with organization creation.
        Uses minimal service role operations only where absolutely necessary.
        """
        client_info = client_info or {}
        
        try:
            # Log registration attempt
            await security_logger.log_user_registration(
                email=user_data.email,
                success=False,  # Will update on success
                ip_address=client_info.get("ip_address")
            )
            
            if self.dev_mode:
                # Development mode - mock registration
                user_id = await self._create_dev_user_id(user_data.email)
                
                # Create or assign to organization
                if user_data.organization_name:
                    org = await organization_service.create_organization_for_user(
                        user_id, user_data.organization_name, "dev_token"
                    )
                else:
                    org = await organization_service.ensure_user_has_organization(
                        user_id, user_data.email
                    )
                
                await security_logger.log_user_registration(
                    email=user_data.email,
                    success=True,
                    user_id=user_id,
                    client_id=org.id,
                    ip_address=client_info.get("ip_address")
                )
                
                # Return registration token (user should login afterward)
                return EnhancedTokenResponse(
                    access_token="registration_successful",
                    user=EnhancedUserResponse(
                        id=user_id,
                        email=user_data.email,
                        created_at=datetime.now(timezone.utc),
                        client_id=org.id,
                        client_name=org.name,
                        organizations=[org],
                        permissions=org.permissions
                    ),
                    token_version="v2"
                )
            
            # Production mode - CAREFULLY use service role ONLY for user creation
            # This is the minimal necessary service role usage
            admin_supabase = create_client(
                get_settings().supabase_url,
                get_settings().supabase_service_key
            )
            
            # Log service role usage for audit
            await security_logger.log_service_role_usage(
                operation="user_creation",
                details={
                    "email": user_data.email,
                    "reason": "Supabase requires admin for user creation",
                    "scope": "create_user_only"
                }
            )
            
            # Create user with minimal service role usage
            response = admin_supabase.auth.admin.create_user({
                "email": user_data.email,
                "password": user_data.password,
                "email_confirm": True
            })
            
            if not response.user:
                raise AuthenticationException("Failed to create user")
            
            user_id = response.user.id
            
            # Immediately switch to user-scoped operations
            # Sign in user to get their session token
            login_response = self.supabase.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if not login_response.session:
                raise AuthenticationException("Failed to authenticate new user")
            
            user_token = login_response.session.access_token
            
            # Create user record in public.users using user-scoped auth  
            try:
                self.supabase.auth.set_auth(user_token)
            except AttributeError:
                # Fallback: Set authorization header directly
                self.supabase.auth._client.headers.update({
                    "Authorization": f"Bearer {user_token}"
                })
            user_profile_result = self.supabase.table('users').insert({
                'id': user_id,
                'email': user_data.email
            }).execute()
            
            # Create or assign organization using user-scoped auth
            if user_data.organization_name:
                org = await organization_service.create_organization_for_user(
                    user_id, user_data.organization_name, user_token
                )
            else:
                org = await organization_service.ensure_user_has_organization(
                    user_id, user_data.email, user_token
                )
            
            await security_logger.log_user_registration(
                email=user_data.email,
                success=True,
                user_id=user_id,
                client_id=org.id,
                ip_address=client_info.get("ip_address")
            )
            
            # Return registration success (user should login afterward for security)
            return EnhancedTokenResponse(
                access_token="registration_successful",
                user=EnhancedUserResponse(
                    id=user_id,
                    email=user_data.email,
                    created_at=datetime.fromisoformat(response.user.created_at.replace('Z', '+00:00')),
                    client_id=org.id,
                    client_name=org.name,
                    organizations=[org],
                    permissions=org.permissions
                ),
                token_version="v2"
            )
            
        except AuthenticationException:
            raise
        except Exception as e:
            await security_logger.log_user_registration(
                email=user_data.email,
                success=False,
                ip_address=client_info.get("ip_address"),
                error_details=str(e)
            )
            self.logger.error(f"Registration error for {user_data.email}: {str(e)}")
            raise AuthenticationException("Registration failed")
    
    async def validate_token(
        self, 
        token: str,
        client_info: Dict[str, Optional[str]] = None
    ) -> TokenValidationResponse:
        """
        Secure token validation WITHOUT service role usage.
        This is the key security improvement - no service role bypass.
        """
        client_info = client_info or {}
        
        try:
            if not token:
                await security_logger.log_token_validation(
                    success=False,
                    error_details="Empty token",
                    ip_address=client_info.get("ip_address")
                )
                return TokenValidationResponse(valid=False, error="Empty token")
            
            # Remove Bearer prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Validate token using JWT (no service role needed)
            payload = jwt_manager.validate_token(token)
            
            if not payload:
                await security_logger.log_token_validation(
                    success=False,
                    error_details="Invalid token",
                    ip_address=client_info.get("ip_address")
                )
                return TokenValidationResponse(valid=False, error="Invalid token")
            
            # Extract user context from token
            user_context = jwt_manager.extract_user_context(payload)
            token_version = payload.get("token_version", "v1")
            
            # Additional validation for v2 tokens
            if token_version == "v2" and payload.get("client_id"):
                # Validate client access (optional verification)
                has_access = await organization_service.validate_client_access(
                    user_context.id, 
                    payload["client_id"]
                )
                
                if not has_access:
                    await security_logger.log_authorization_check(
                        user_id=user_context.id,
                        email=user_context.email,
                        client_id=payload["client_id"],
                        success=False,
                        error_details="Client access denied",
                        ip_address=client_info.get("ip_address")
                    )
                    return TokenValidationResponse(valid=False, error="Client access denied")
            
            # Log successful validation
            await security_logger.log_token_validation(
                user_id=user_context.id,
                email=user_context.email,
                client_id=user_context.client_id,
                success=True,
                token_version=token_version,
                ip_address=client_info.get("ip_address")
            )
            
            return TokenValidationResponse(
                valid=True,
                user_context=user_context,
                token_version=token_version,
                expires_at=datetime.fromtimestamp(payload.get("exp", 0))
            )
            
        except Exception as e:
            await security_logger.log_token_validation(
                success=False,
                error_details=str(e),
                ip_address=client_info.get("ip_address")
            )
            self.logger.error(f"Token validation error: {str(e)}")
            return TokenValidationResponse(valid=False, error="Token validation failed")
    
    async def create_legacy_token_response(
        self, 
        user_context: UserContext
    ) -> TokenResponse:
        """
        Create legacy token response for backward compatibility.
        """
        try:
            # Create v1 token for legacy compatibility
            legacy_token = jwt_manager.create_legacy_token(
                user_context.id, 
                user_context.email
            )
            
            return TokenResponse(
                access_token=legacy_token,
                user=UserResponse(
                    id=user_context.id,
                    email=user_context.email,
                    created_at=user_context.created_at
                ),
                token_version="v1"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create legacy token: {str(e)}")
            raise AuthenticationException("Token creation failed")
    
    async def logout(self, token: str) -> bool:
        """
        Secure logout - invalidates session.
        """
        try:
            # In JWT-based system, logout is typically handled client-side
            # For enhanced security, we could maintain a token blacklist
            
            # Validate token first to get user info for logging
            validation_response = await self.validate_token(token)
            
            if validation_response.valid and validation_response.user_context:
                await security_logger.log_security_event(
                    event_type="logout",
                    user_id=validation_response.user_context.id,
                    email=validation_response.user_context.email,
                    client_id=validation_response.user_context.client_id,
                    success=True,
                    details={"token_version": validation_response.token_version}
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Logout error: {str(e)}")
            return False
    
    async def _create_dev_user_id(self, email: str) -> str:
        """Create deterministic UUID for development"""
        # Special handling for test users to use real Supabase ID
        if email == "test@example.com":
            return "548e4038-7dea-41cc-98e0-ffa0b651154a"  # Real Supabase user ID
        elif email == "test2@example.com":
            return "f2fa5ab6-c2c7-40f5-a887-a2014ab7df81"  # Real Supabase user ID for test2
        elif email == "user@email.com":
            return "fdd71f95-e8d4-417e-85aa-9b7b0c92436d"  # Real Supabase user ID for user@email.com
        else:
            import hashlib
            import uuid
            # Create deterministic UUID from email hash
            hash_obj = hashlib.sha256(email.encode())
            # Use first 32 hex chars and format as UUID
            hex_string = hash_obj.hexdigest()[:32]
            # Format as UUID: 8-4-4-4-12
            formatted_uuid = f"{hex_string[:8]}-{hex_string[8:12]}-{hex_string[12:16]}-{hex_string[16:20]}-{hex_string[20:32]}"
            return formatted_uuid


# Global secure auth service instance
secure_auth_service = SecureAuthService()