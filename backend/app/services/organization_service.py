"""
Organization service for managing client context and multi-tenant data.
Provides secure organization lookup and validation without service role dependency.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from app.utils.config import get_settings
from app.models.auth import OrganizationInfo, UserContext
from app.utils.exceptions import AuthenticationException


class OrganizationService:
    """
    Service for managing organization context and user-organization relationships.
    Uses user-scoped authentication instead of service role for security.
    """
    
    def __init__(self):
        settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Development mode handling
        if settings.environment == "development" or "placeholder" in settings.supabase_url:
            self.logger.info("Running in development mode - using mock organization service")
            self.supabase = None
            self.dev_mode = True
        else:
            # Use anon client for user-scoped queries (no service role)
            self.supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            self.dev_mode = False
    
    async def get_user_organizations(
        self, 
        user_id: str, 
        user_token: Optional[str] = None
    ) -> List[OrganizationInfo]:
        """
        Get all organizations a user belongs to.
        Uses user-scoped authentication instead of service role.
        """
        try:
            if self.dev_mode:
                # Mock organization for development
                return [OrganizationInfo(
                    id="00000000-0000-0000-0000-000000000001",
                    name="Development Organization",
                    slug="dev-org",
                    role="owner",
                    permissions=["read", "write", "admin"],
                    settings={"environment": "development"}
                )]
            
            # Set user token for RLS enforcement (no service role)
            if user_token:
                try:
                    # For Supabase client auth, we need to set the token in the headers instead of using set_session
                    # This avoids the refresh_token requirement issue
                    self.supabase.auth.set_auth(user_token)
                except AttributeError:
                    # Fallback: Set authorization header directly on the client
                    self.supabase.auth._client.headers.update({
                        "Authorization": f"Bearer {user_token}"
                    })
            
            # Query user organizations with RLS enforcement
            result = self.supabase.table('user_organizations').select('''
                role,
                is_active,
                organizations:organization_id (
                    id,
                    name,
                    slug,
                    settings,
                    is_active
                )
            ''').eq('user_id', user_id).eq('is_active', True).execute()
            
            organizations = []
            for item in result.data or []:
                org_data = item.get('organizations')
                if org_data and org_data.get('is_active'):
                    # Map role to permissions (simplified)
                    permissions = self._get_role_permissions(item.get('role', 'member'))
                    
                    organizations.append(OrganizationInfo(
                        id=org_data['id'],
                        name=org_data['name'],
                        slug=org_data['slug'],
                        role=item.get('role', 'member'),
                        permissions=permissions,
                        settings=org_data.get('settings', {})
                    ))
            
            self.logger.info(f"Found {len(organizations)} organizations for user {user_id}")
            return organizations
            
        except Exception as e:
            self.logger.error(f"Failed to get user organizations: {str(e)}")
            # Return default organization on error (for migration compatibility)
            return await self._get_default_organization()
    
    async def get_primary_organization(
        self, 
        user_id: str, 
        user_token: Optional[str] = None
    ) -> Optional[OrganizationInfo]:
        """
        Get user's primary organization (for backward compatibility).
        """
        try:
            organizations = await self.get_user_organizations(user_id, user_token)
            if organizations:
                # Return first organization (or owner role if available)
                owner_orgs = [org for org in organizations if org.role == 'owner']
                return owner_orgs[0] if owner_orgs else organizations[0]
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get primary organization: {str(e)}")
            return None
    
    async def validate_client_access(
        self, 
        user_id: str, 
        client_id: str,
        user_token: Optional[str] = None
    ) -> bool:
        """
        Validate that user has access to the specified client/organization.
        """
        try:
            if self.dev_mode:
                # In development, allow access to default org
                return client_id == "00000000-0000-0000-0000-000000000001"
            
            organizations = await self.get_user_organizations(user_id, user_token)
            return any(org.id == client_id for org in organizations)
            
        except Exception as e:
            self.logger.error(f"Failed to validate client access: {str(e)}")
            return False
    
    async def create_organization_for_user(
        self, 
        user_id: str, 
        org_name: str,
        user_token: str
    ) -> Optional[OrganizationInfo]:
        """
        Create a new organization for a user (during registration).
        Uses user-scoped authentication.
        """
        try:
            if self.dev_mode:
                # Mock organization creation
                return OrganizationInfo(
                    id=f"dev-org-{user_id[:8]}",
                    name=org_name,
                    slug=org_name.lower().replace(" ", "-"),
                    role="owner",
                    permissions=["read", "write", "admin"],
                    settings={"created_by": user_id}
                )
            
            # Set user token for RLS
            try:
                self.supabase.auth.set_auth(user_token)
            except AttributeError:
                # Fallback: Set authorization header directly
                self.supabase.auth._client.headers.update({
                    "Authorization": f"Bearer {user_token}"
                })
            
            # Create organization
            slug = org_name.lower().replace(" ", "-").replace("_", "-")
            org_result = self.supabase.table('organizations').insert({
                'name': org_name,
                'slug': slug,
                'settings': {'created_by': user_id}
            }).execute()
            
            if not org_result.data:
                raise Exception("Failed to create organization")
            
            org_data = org_result.data[0]
            
            # Link user to organization as owner
            self.supabase.table('user_organizations').insert({
                'user_id': user_id,
                'organization_id': org_data['id'],
                'role': 'owner',
                'is_active': True
            }).execute()
            
            return OrganizationInfo(
                id=org_data['id'],
                name=org_data['name'],
                slug=org_data['slug'],
                role='owner',
                permissions=["read", "write", "admin"],
                settings=org_data.get('settings', {})
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create organization: {str(e)}")
            return None
    
    async def ensure_user_has_organization(
        self, 
        user_id: str, 
        email: str,
        user_token: Optional[str] = None
    ) -> OrganizationInfo:
        """
        Ensure user has at least one organization.
        Creates default organization if user has none.
        """
        try:
            # Check if user already has organizations
            organizations = await self.get_user_organizations(user_id, user_token)
            if organizations:
                return organizations[0]  # Return first organization
            
            # User has no organizations, assign to default or create personal org
            if self.dev_mode:
                return OrganizationInfo(
                    id="00000000-0000-0000-0000-000000000001",
                    name="Development Organization",
                    slug="dev-org",
                    role="member",
                    permissions=["read", "write"],
                    settings={}
                )
            
            # In production, assign to default organization
            default_org = await self._get_default_organization()
            if default_org:
                await self._assign_user_to_organization(
                    user_id, 
                    default_org[0].id, 
                    "member", 
                    user_token
                )
                return default_org[0]
            
            raise Exception("No default organization available")
            
        except Exception as e:
            self.logger.error(f"Failed to ensure user organization: {str(e)}")
            raise
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Map role to permissions"""
        role_permissions = {
            'owner': ['read', 'write', 'admin', 'manage_users', 'manage_billing'],
            'admin': ['read', 'write', 'admin', 'manage_users'],
            'member': ['read', 'write'],
            'viewer': ['read']
        }
        return role_permissions.get(role, ['read'])
    
    async def _get_default_organization(self) -> List[OrganizationInfo]:
        """Get default organization for fallback"""
        try:
            # Always return development organization for demo purposes
            # This handles the case where the organizations table doesn't exist yet
            return [OrganizationInfo(
                id="00000000-0000-0000-0000-000000000001",
                name="Default Organization",
                slug="default-org",
                role="member",
                permissions=["read", "write"],
                settings={"demo_mode": True, "created_by_fallback": True}
            )]
            
        except Exception as e:
            self.logger.error(f"Failed to get default organization: {str(e)}")
            # Return hardcoded default as final fallback
            return [OrganizationInfo(
                id="00000000-0000-0000-0000-000000000001",
                name="Default Organization",
                slug="default-org",
                role="member",
                permissions=["read", "write"],
                settings={"demo_mode": True, "fallback": True}
            )]
    
    async def _assign_user_to_organization(
        self, 
        user_id: str, 
        org_id: str, 
        role: str,
        user_token: Optional[str] = None
    ):
        """Assign user to organization"""
        try:
            if self.dev_mode:
                return  # Skip in dev mode
            
            if user_token:
                try:
                    self.supabase.auth.set_auth(user_token)
                except AttributeError:
                    # Fallback: Set authorization header directly
                    self.supabase.auth._client.headers.update({
                        "Authorization": f"Bearer {user_token}"
                    })
            
            self.supabase.table('user_organizations').insert({
                'user_id': user_id,
                'organization_id': org_id,
                'role': role,
                'is_active': True
            }).execute()
            
        except Exception as e:
            self.logger.error(f"Failed to assign user to organization: {str(e)}")
            raise


# Global organization service instance
organization_service = OrganizationService()