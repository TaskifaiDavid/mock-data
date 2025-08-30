"""
Authentication Migration Wrapper - Phase 3 Backward Compatibility.

This service provides backward compatibility between the old service-role-based 
authentication and the new secure client-context-aware authentication during 
the migration period.

Features:
- Supports both v1 (legacy) and v2 (secure) token formats
- Gradual migration of existing sessions
- Fallback mechanisms for compatibility
- Migration progress tracking
"""

import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime
from app.models.auth import (
    UserLogin, UserRegister, TokenResponse, EnhancedTokenResponse,
    UserResponse, UserInDB, TokenValidationResponse, UserContext
)
from app.services.auth_service import auth_service as legacy_auth_service
from app.services.secure_auth_service import secure_auth_service
from app.services.security_logger import security_logger
from app.utils.jwt_utils import jwt_manager


class AuthMigrationWrapper:
    """
    Wrapper service that handles both legacy and new authentication during migration.
    Provides seamless transition while maintaining backward compatibility.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.migration_enabled = True  # Enable migration features
        self.force_v2_for_new_logins = True  # New logins use v2 by default
        
    async def login(
        self, 
        credentials: UserLogin,
        client_info: Dict[str, Optional[str]] = None,
        force_version: Optional[str] = None
    ) -> Union[TokenResponse, EnhancedTokenResponse]:
        """
        Login with version negotiation.
        New logins use v2 by default, but can fall back to v1 if needed.
        """
        try:
            # Determine which version to use
            use_v2 = (force_version == "v2") or (
                force_version != "v1" and self.force_v2_for_new_logins
            )
            
            if use_v2:
                try:
                    # Attempt v2 login first
                    response = await secure_auth_service.login(credentials, client_info)
                    
                    # Log successful v2 migration
                    await security_logger.log_login_attempt(
                        email=credentials.email,
                        success=True,
                        error_details="login_v2_success"
                    )
                    
                    return response
                    
                except Exception as e:
                    self.logger.warning(f"v2 login failed for {credentials.email}, falling back to v1: {str(e)}")
                    
                    # Log v2 failure and fallback
                    await security_logger.log_login_attempt(
                        email=credentials.email,
                        success=False,
                        error_details=f"login_v2_fallback: {str(e)}"
                    )
            
            # Use v1 (legacy) authentication
            legacy_response = await legacy_auth_service.login(credentials)
            
            # Log v1 usage
            await security_logger.log_login_attempt(
                email=credentials.email,
                success=True,
                user_id=legacy_response.user.id,
                error_details="login_v1_used"
            )
            
            return legacy_response
            
        except Exception as e:
            self.logger.error(f"All login methods failed for {credentials.email}: {str(e)}")
            raise
    
    async def register(
        self, 
        user_data: UserRegister,
        client_info: Dict[str, Optional[str]] = None,
        force_version: Optional[str] = None
    ) -> Union[TokenResponse, EnhancedTokenResponse]:
        """
        Registration with version preference.
        New registrations use v2 by default for enhanced security.
        """
        try:
            # Always prefer v2 for new registrations for better security
            use_v2 = force_version != "v1"
            
            if use_v2:
                try:
                    response = await secure_auth_service.register(user_data, client_info)
                    
                    # Log successful v2 registration
                    await security_logger.log_user_registration(
                        email=user_data.email,
                        success=True,
                        error_details="register_v2_success"
                    )
                    
                    return response
                    
                except Exception as e:
                    self.logger.warning(f"v2 registration failed for {user_data.email}, falling back to v1: {str(e)}")
                    
                    # Log fallback
                    await security_logger.log_user_registration(
                        email=user_data.email,
                        success=False,
                        error_details=f"register_v2_fallback: {str(e)}"
                    )
            
            # Fallback to v1 registration
            legacy_response = await legacy_auth_service.register(user_data)
            
            # Log v1 usage
            await security_logger.log_user_registration(
                email=user_data.email,
                success=True,
                error_details="register_v1_used"
            )
            
            return legacy_response
            
        except Exception as e:
            self.logger.error(f"All registration methods failed for {user_data.email}: {str(e)}")
            raise
    
    async def verify_token(
        self, 
        token: str,
        client_info: Dict[str, Optional[str]] = None,
        prefer_v2: bool = True
    ) -> Optional[Union[Dict[str, Any], UserContext]]:
        """
        Token verification with automatic version detection and migration.
        Supports both v1 and v2 tokens seamlessly.
        """
        try:
            if not token:
                return None
            
            # Remove Bearer prefix if present
            clean_token = token[7:] if token.startswith('Bearer ') else token
            
            # Detect token version
            token_version = jwt_manager.get_token_version(clean_token)
            
            if token_version == "v2" or (prefer_v2 and token_version == "unknown"):
                # Try v2 validation first
                try:
                    validation_response = await secure_auth_service.validate_token(
                        clean_token, client_info
                    )
                    
                    if validation_response.valid:
                        # Log successful v2 validation
                        await security_logger.log_token_validation(
                            user_id=validation_response.user_context.id,
                            email=validation_response.user_context.email,
                            client_id=validation_response.user_context.client_id,
                            success=True,
                            token_version="v2"
                        )
                        
                        return validation_response.user_context
                    
                except Exception as e:
                    self.logger.debug(f"v2 token validation failed, trying v1: {str(e)}")
            
            # Try v1 (legacy) validation
            try:
                legacy_user_data = await legacy_auth_service.verify_token(clean_token)
                
                if legacy_user_data:
                    # Log v1 token usage for migration tracking
                    await security_logger.log_token_validation(
                        user_id=legacy_user_data.get("id"),
                        email=legacy_user_data.get("email"),
                        success=True,
                        token_version="v1"
                    )
                    
                    # Consider upgrading v1 tokens to v2 during validation
                    if self.should_upgrade_token(legacy_user_data):
                        upgraded_context = await self._upgrade_v1_to_v2_context(legacy_user_data)
                        if upgraded_context:
                            return upgraded_context
                    
                    return legacy_user_data
                
            except Exception as e:
                self.logger.debug(f"v1 token validation also failed: {str(e)}")
            
            # Both methods failed
            await security_logger.log_token_validation(
                success=False,
                error_details="Token validation failed for both v1 and v2"
            )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Token verification error: {str(e)}")
            return None
    
    async def get_current_user_compatible(
        self, 
        token: str,
        client_info: Dict[str, Optional[str]] = None
    ) -> UserInDB:
        """
        Get current user in format compatible with existing dependencies.
        Handles both v1 and v2 tokens and returns UserInDB format.
        """
        try:
            user_data = await self.verify_token(token, client_info)
            
            if not user_data:
                return None
            
            # Handle both UserContext (v2) and dict (v1) formats
            if isinstance(user_data, UserContext):
                # v2 UserContext
                return UserInDB(
                    id=user_data.id,
                    email=user_data.email,
                    created_at=user_data.created_at,
                    client_id=user_data.client_id,
                    organizations=user_data.organizations,
                    permissions=user_data.global_permissions
                )
            else:
                # v1 dict format
                return UserInDB(
                    id=user_data["id"],
                    email=user_data["email"],
                    created_at=user_data.get("created_at"),
                    client_id=None,  # v1 tokens don't have client_id
                    organizations=[],
                    permissions=[]
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get current user: {str(e)}")
            return None
    
    def should_upgrade_token(self, legacy_user_data: Dict[str, Any]) -> bool:
        """
        Determine if a v1 token should be upgraded to v2.
        Currently conservative - only upgrade in specific conditions.
        """
        # For now, don't auto-upgrade to avoid breaking existing sessions
        # This could be enabled gradually based on user activity patterns
        return False
    
    async def _upgrade_v1_to_v2_context(
        self, 
        legacy_user_data: Dict[str, Any]
    ) -> Optional[UserContext]:
        """
        Upgrade v1 token data to v2 UserContext format.
        This requires fetching organization data.
        """
        try:
            user_id = legacy_user_data["id"]
            email = legacy_user_data["email"]
            
            # Fetch organization data (this might require service role in some cases)
            from app.services.organization_service import organization_service
            organizations = await organization_service.get_user_organizations(user_id)
            
            # Create v2 UserContext
            return UserContext(
                id=user_id,
                email=email,
                created_at=datetime.fromisoformat(
                    legacy_user_data.get("created_at", datetime.utcnow().isoformat())
                ),
                client_id=organizations[0].id if organizations else None,
                client_name=organizations[0].name if organizations else None,
                organizations=organizations,
                global_permissions=organizations[0].permissions if organizations else []
            )
            
        except Exception as e:
            self.logger.error(f"Failed to upgrade v1 to v2 context: {str(e)}")
            return None
    
    async def logout(self, token: str) -> bool:
        """
        Logout supporting both token versions.
        """
        try:
            # Try both v2 and v1 logout methods
            v2_success = await secure_auth_service.logout(token)
            v1_success = await legacy_auth_service.logout(token)
            
            return v2_success or v1_success
            
        except Exception as e:
            self.logger.error(f"Logout error: {str(e)}")
            return False
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """
        Get migration status and statistics.
        Useful for monitoring migration progress.
        """
        return {
            "migration_enabled": self.migration_enabled,
            "force_v2_for_new_logins": self.force_v2_for_new_logins,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "phase_3_auth_migration"
        }


# Global migration wrapper instance
auth_migration_wrapper = AuthMigrationWrapper()