from fastapi import APIRouter, Depends, Header
from app.models.auth import UserLogin, UserRegister, TokenResponse
from app.services.auth_service import AuthService
from app.utils.exceptions import AuthenticationException
from typing import Optional
import logging

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

async def get_auth_service() -> AuthService:
    return AuthService()

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login(credentials)

@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register(user_data)

@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationException("Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    success = await auth_service.logout(token)
    return {"success": success}

@router.get("/debug-token")
async def debug_token(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Debug endpoint to check token validity and provide diagnostics"""
    import os
    
    # Security: Only allow debug endpoint in development environment
    if os.getenv("ENVIRONMENT", "development") == "production":
        raise AuthenticationException("Debug endpoint not available in production")
    
    debug_info = {
        "timestamp": str(__import__('datetime').datetime.now()),
        "authorization_header_provided": authorization is not None,
        "authorization_header_length": len(authorization) if authorization else 0,
        "authorization_header_format": "valid" if authorization and authorization.startswith("Bearer ") else "invalid",
        "token_extracted": False,
        "token_length": 0,
        "user_found": False,
        "error": None
    }
    
    try:
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            debug_info["token_extracted"] = True
            debug_info["token_length"] = len(token)
            debug_info["token_preview"] = f"***...{token[-4:]}" if len(token) > 10 else "***"
            
            user = await auth_service.verify_token(token)
            debug_info["user_found"] = user is not None
            if user:
                debug_info["user_email"] = user.get("email", "unknown")
                debug_info["user_id"] = user.get("id", "unknown")
        
        return debug_info
        
    except Exception as e:
        debug_info["error"] = str(e)
        return debug_info

async def get_current_user(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    logger.info("get_current_user called")
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
        
        user = await auth_service.verify_token(token)
        
        if not user:
            logger.warning("Token verification returned no user")
            raise AuthenticationException("Invalid or expired token")
        
        logger.info(f"Successfully authenticated user: {user.get('email', 'unknown')}")
        return user
        
    except IndexError:
        logger.error("Failed to extract token from authorization header")
        raise AuthenticationException("Malformed authorization header")
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise AuthenticationException("Authentication failed")