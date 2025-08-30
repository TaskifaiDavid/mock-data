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
        if settings.environment == "development":
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
                    # Special handling for test users to use real Supabase ID
                    if credentials.email == "test@example.com":
                        user_id = "548e4038-7dea-41cc-98e0-ffa0b651154a"  # Real Supabase user ID
                    elif credentials.email == "test2@example.com":
                        user_id = "f2fa5ab6-c2c7-40f5-a887-a2014ab7df81"  # Real Supabase user ID for test2
                    elif credentials.email == "user@email.com":
                        user_id = "fdd71f95-e8d4-417e-85aa-9b7b0c92436d"  # Real Supabase user ID for user@email.com
                    else:
                        # Create unique UUID based on email hash to prevent cross-user data exposure
                        import hashlib
                        # Create deterministic UUID from email hash
                        hash_obj = hashlib.sha256(credentials.email.encode())
                        hex_string = hash_obj.hexdigest()[:32]
                        # Format as UUID: 8-4-4-4-12
                        user_id = f"{hex_string[:8]}-{hex_string[8:12]}-{hex_string[12:16]}-{hex_string[16:20]}-{hex_string[20:32]}"
                    return TokenResponse(
                        access_token=f"dev_token_{credentials.email}",
                        user=UserResponse(
                            id=user_id,
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
                # Development mode - mock registration with unique user ID
                # Special handling for test users to use real Supabase ID
                if user_data.email == "test@example.com":
                    user_id = "548e4038-7dea-41cc-98e0-ffa0b651154a"  # Real Supabase user ID
                elif user_data.email == "test2@example.com":
                    user_id = "f2fa5ab6-c2c7-40f5-a887-a2014ab7df81"  # Real Supabase user ID for test2
                elif user_data.email == "user@email.com":
                    user_id = "fdd71f95-e8d4-417e-85aa-9b7b0c92436d"  # Real Supabase user ID for user@email.com
                else:
                    import hashlib
                    # Create deterministic UUID from email hash
                    hash_obj = hashlib.sha256(user_data.email.encode())
                    hex_string = hash_obj.hexdigest()[:32]
                    # Format as UUID: 8-4-4-4-12
                    user_id = f"{hex_string[:8]}-{hex_string[8:12]}-{hex_string[12:16]}-{hex_string[16:20]}-{hex_string[20:32]}"
                return TokenResponse(
                    access_token="registration_successful",
                    user=UserResponse(
                        id=user_id,
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
                # Development mode - mock token verification with unique user ID
                if token.startswith('dev_token_'):
                    email = token.replace('dev_token_', '')
                    import hashlib
                    # Create deterministic UUID from email hash
                    hash_obj = hashlib.sha256(email.encode())
                    hex_string = hash_obj.hexdigest()[:32]
                    # Format as UUID: 8-4-4-4-12
                    user_id = f"{hex_string[:8]}-{hex_string[8:12]}-{hex_string[12:16]}-{hex_string[16:20]}-{hex_string[20:32]}"
                    return {
                        'id': user_id,
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
    FastAPI dependency to get the current authenticated user from JWT token.
    Enhanced with v1/v2 token support and client context.
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Use migration wrapper for enhanced authentication
        from app.services.auth_migration_wrapper import auth_migration_wrapper
        user = await auth_migration_wrapper.get_current_user_compatible(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )