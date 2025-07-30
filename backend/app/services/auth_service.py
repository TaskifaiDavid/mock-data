from supabase import create_client, Client
from app.utils.config import get_settings
from app.utils.exceptions import AuthenticationException
from app.models.auth import UserLogin, UserRegister, UserResponse, TokenResponse, UserInDB
from typing import Optional
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class AuthService:
    def __init__(self):
        settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Development mode - use mock authentication
        if settings.environment == "development" or "placeholder" in settings.supabase_url:
            self.logger.info("Running in development mode - using mock authentication")
            self.supabase = None
            self.admin_supabase = None
            self.dev_mode = True
        else:
            self.supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            self.admin_supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_key
            )
            self.dev_mode = False
    
    async def login(self, credentials: UserLogin) -> TokenResponse:
        try:
            if self.dev_mode:
                # Development mode - mock authentication
                if credentials.email and credentials.password:
                    return TokenResponse(
                        access_token=f"dev_token_{credentials.email}",
                        user=UserResponse(
                            id="dev_user_123",
                            email=credentials.email,
                            created_at="2025-01-01T00:00:00Z"
                        )
                    )
                else:
                    raise AuthenticationException("Email and password required")
            
            # Production mode - use Supabase
            response = self.supabase.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })
            
            if not response.user:
                raise AuthenticationException("Invalid credentials")
            
            return TokenResponse(
                access_token=response.session.access_token,
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    created_at=response.user.created_at
                )
            )
        except Exception as e:
            if not self.dev_mode:
                raise AuthenticationException(str(e))
            else:
                raise AuthenticationException("Invalid credentials")
    
    async def register(self, user_data: UserRegister) -> TokenResponse:
        try:
            if self.dev_mode:
                # Development mode - mock registration
                return TokenResponse(
                    access_token="registration_successful",
                    user=UserResponse(
                        id="dev_user_new",
                        email=user_data.email,
                        created_at="2025-01-01T00:00:00Z"
                    )
                )
            
            # Production mode - use Supabase
            # Create user with admin client
            response = self.admin_supabase.auth.admin.create_user({
                "email": user_data.email,
                "password": user_data.password,
                "email_confirm": True
            })
            
            if not response.user:
                raise AuthenticationException("Failed to create user")
            
            # Create user profile in public.users table
            user_profile = self.admin_supabase.table('users').insert({
                'id': response.user.id,
                'email': response.user.email
            }).execute()
            
            # For security, return user info without session token
            # User should login after registration
            return TokenResponse(
                access_token="registration_successful",
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    created_at=response.user.created_at
                )
            )
        except Exception as e:
            raise AuthenticationException(str(e))
    
    async def verify_token(self, token: str) -> Optional[dict]:
        try:
            self.logger.info(f"Attempting token verification for token ending with: ...{token[-4:]}")
            
            if not token:
                self.logger.warning("Empty token provided for verification")
                return None
            
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
                self.logger.debug("Removed Bearer prefix from token")
            
            if self.dev_mode:
                # Development mode - mock token verification
                if token.startswith('dev_token_'):
                    email = token.replace('dev_token_', '')
                    return {
                        'id': 'dev_user_123',
                        'email': email,
                        'created_at': '2025-01-01T00:00:00Z'
                    }
                else:
                    return None
            
            # Production mode - use Supabase
            # Use admin/service client for token validation as it has proper permissions
            self.logger.debug("Using admin client for token validation")
            response = self.admin_supabase.auth.get_user(token)
            
            if response.user:
                self.logger.info(f"Token verification successful for user: {response.user.email}")
                return response.user.model_dump()
            else:
                self.logger.warning("Token verification failed - no user returned")
                return None
                
        except Exception as e:
            self.logger.error(f"Token verification error: {str(e)}")
            self.logger.error(f"Token type: {type(token)}")
            self.logger.error(f"Token length: {len(token) if token else 'None'}")
            if hasattr(e, 'response'):
                self.logger.error(f"Response status: {getattr(e.response, 'status_code', 'Unknown')}")
                self.logger.error(f"Response text: {getattr(e.response, 'text', 'Unknown')}")
            return None
    
    async def logout(self, token: str) -> bool:
        try:
            self.supabase.auth.sign_out()
            return True
        except Exception:
            return False

# Create a global auth service instance
auth_service = AuthService()

# HTTP Bearer token security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """
    FastAPI dependency to get the current authenticated user from JWT token
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify token using auth service
        user_data = await auth_service.verify_token(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert to UserInDB model
        return UserInDB(
            id=user_data["id"],
            email=user_data["email"],
            created_at=user_data.get("created_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )