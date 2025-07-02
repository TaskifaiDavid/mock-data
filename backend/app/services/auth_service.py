from supabase import create_client, Client
from app.utils.config import get_settings
from app.utils.exceptions import AuthenticationException
from app.models.auth import UserLogin, UserRegister, UserResponse, TokenResponse
from typing import Optional
import logging

class AuthService:
    def __init__(self):
        settings = get_settings()
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        self.admin_supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        self.logger = logging.getLogger(__name__)
    
    async def login(self, credentials: UserLogin) -> TokenResponse:
        try:
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
            raise AuthenticationException(str(e))
    
    async def register(self, user_data: UserRegister) -> TokenResponse:
        try:
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
            self.logger.info(f"Attempting token verification for token starting with: {token[:20]}...")
            
            if not token:
                self.logger.warning("Empty token provided for verification")
                return None
            
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
                self.logger.debug("Removed Bearer prefix from token")
            
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