from fastapi import APIRouter, Depends, Header
from app.models.auth import UserLogin, UserRegister, TokenResponse
from app.services.auth_service import AuthService
from app.utils.exceptions import AuthenticationException
from typing import Optional

router = APIRouter(prefix="/auth", tags=["authentication"])

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

async def get_current_user(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationException("Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    user = await auth_service.verify_token(token)
    
    if not user:
        raise AuthenticationException("Invalid token")
    
    return user