from fastapi import APIRouter, Depends, Header, Request
from app.models.auth import UserLogin, UserRegister, TokenResponse, EnhancedTokenResponse
from app.services.auth_service import AuthService
from app.services.auth_migration_wrapper import auth_migration_wrapper
from app.services.security_logger import security_logger
from app.utils.exceptions import AuthenticationException
from typing import Optional, Union
import logging

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

async def get_auth_service() -> AuthService:
    return AuthService()

def extract_client_info(request: Request) -> dict:
    """Extract client information for security logging"""
    return security_logger.get_client_info(request)

@router.post("/login", response_model=Union[TokenResponse, EnhancedTokenResponse])
async def login(
    credentials: UserLogin,
    request: Request,
    version: Optional[str] = Header(None, alias="X-Auth-Version"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Enhanced login with multi-tenant support and backward compatibility.
    
    Headers:
    - X-Auth-Version: "v1" (legacy) or "v2" (enhanced) - defaults to v2
    """
    client_info = extract_client_info(request)
    
    # Use migration wrapper for seamless v1/v2 support
    return await auth_migration_wrapper.login(
        credentials, 
        client_info, 
        force_version=version
    )

@router.post("/register", response_model=Union[TokenResponse, EnhancedTokenResponse])
async def register(
    user_data: UserRegister,
    request: Request,
    version: Optional[str] = Header(None, alias="X-Auth-Version"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Enhanced registration with organization support and backward compatibility.
    
    Body:
    - organization_name: Optional organization name for new users
    
    Headers:
    - X-Auth-Version: "v1" (legacy) or "v2" (enhanced) - defaults to v2
    """
    client_info = extract_client_info(request)
    
    # Use migration wrapper for seamless v1/v2 support
    return await auth_migration_wrapper.register(
        user_data, 
        client_info, 
        force_version=version
    )

@router.post("/logout")
async def logout(
    request: Request,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Enhanced logout with security logging and v1/v2 support.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationException("Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    client_info = extract_client_info(request)
    
    # Use migration wrapper for logout
    success = await auth_migration_wrapper.logout(token)
    
    return {
        "success": success,
        "message": "Logged out successfully" if success else "Logout failed"
    }

@router.get("/debug-token")
async def debug_token(
    request: Request,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Enhanced debug endpoint with v1/v2 token support and security logging.
    Provides comprehensive token diagnostics for troubleshooting.
    """
    from app.utils.jwt_utils import jwt_manager
    
    client_info = extract_client_info(request)
    debug_info = {
        "timestamp": str(__import__('datetime').datetime.now()),
        "authorization_header_provided": authorization is not None,
        "authorization_header_length": len(authorization) if authorization else 0,
        "authorization_header_format": "valid" if authorization and authorization.startswith("Bearer ") else "invalid",
        "token_extracted": False,
        "token_length": 0,
        "token_version": "unknown",
        "user_found": False,
        "client_context": None,
        "error": None
    }
    
    try:
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            debug_info["token_extracted"] = True
            debug_info["token_length"] = len(token)
            debug_info["token_preview"] = f"***...{token[-4:]}" if len(token) > 10 else "***"
            debug_info["token_version"] = jwt_manager.get_token_version(token)
            debug_info["token_expired"] = jwt_manager.is_token_expired(token)
            
            # Use migration wrapper for comprehensive validation
            user_data = await auth_migration_wrapper.verify_token(token, client_info)
            debug_info["user_found"] = user_data is not None
            
            if user_data:
                if hasattr(user_data, 'email'):  # UserContext (v2)
                    debug_info["user_email"] = user_data.email
                    debug_info["user_id"] = user_data.id
                    debug_info["client_context"] = {
                        "client_id": user_data.client_id,
                        "client_name": user_data.client_name,
                        "organizations": len(user_data.organizations),
                        "permissions": user_data.global_permissions
                    }
                else:  # dict (v1)
                    debug_info["user_email"] = user_data.get("email", "unknown")
                    debug_info["user_id"] = user_data.get("id", "unknown")
                    debug_info["client_context"] = {"legacy": True, "no_client_context": True}
        
        return debug_info
        
    except Exception as e:
        debug_info["error"] = str(e)
        return debug_info

async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Enhanced get_current_user with v1/v2 token support and security logging.
    Returns UserInDB compatible format for existing code.
    """
    logger.info("get_current_user called (enhanced)")
    logger.info(f"Authorization header: {'Present' if authorization else 'None'}")
    
    if not authorization:
        logger.warning("No authorization header provided")
        raise AuthenticationException("Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        logger.warning("Invalid authorization header format")
        raise AuthenticationException("Invalid authorization header format")
    
    try:
        token = authorization.split(" ")[1]
        logger.info(f"Extracted token length: {len(token)}")
        
        client_info = extract_client_info(request)
        
        # Use migration wrapper for enhanced authentication
        user = await auth_migration_wrapper.get_current_user_compatible(token, client_info)
        
        if not user:
            logger.warning("Token verification returned no user")
            raise AuthenticationException("Invalid or expired token")
        
        logger.info(f"Successfully authenticated user: {user.email} (client: {user.client_id or 'legacy'})")
        return user
        
    except IndexError:
        logger.error("Failed to extract token from authorization header")
        raise AuthenticationException("Malformed authorization header")
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise AuthenticationException("Authentication failed")


# Add new endpoints for Phase 3 functionality

@router.get("/migration-status")
async def get_migration_status():
    """
    Get authentication migration status and statistics.
    """
    return await auth_migration_wrapper.get_migration_status()

@router.post("/validate-token")
async def validate_token(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Dedicated token validation endpoint with comprehensive diagnostics.
    Supports both v1 and v2 tokens.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationException("Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    client_info = extract_client_info(request)
    
    # Use secure validation service
    from app.services.secure_auth_service import secure_auth_service
    validation_response = await secure_auth_service.validate_token(token, client_info)
    
    if not validation_response.valid:
        raise AuthenticationException(validation_response.error or "Token validation failed")
    
    return {
        "valid": validation_response.valid,
        "token_version": validation_response.token_version,
        "expires_at": validation_response.expires_at,
        "user": {
            "id": validation_response.user_context.id,
            "email": validation_response.user_context.email,
            "client_id": validation_response.user_context.client_id,
            "client_name": validation_response.user_context.client_name,
            "organizations": len(validation_response.user_context.organizations),
            "permissions": validation_response.user_context.global_permissions
        }
    }