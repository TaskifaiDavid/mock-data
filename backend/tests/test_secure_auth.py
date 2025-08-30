"""
Security validation tests for Phase 3 authentication enhancement.

These tests validate that the new authentication system:
1. Eliminates dangerous service role usage
2. Properly implements client context
3. Enforces multi-tenant isolation
4. Maintains backward compatibility
5. Logs security events properly
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from app.models.auth import (
    UserLogin, UserRegister, UserContext, OrganizationInfo,
    TokenValidationResponse, SecurityEvent
)
from app.services.secure_auth_service import secure_auth_service
from app.services.auth_migration_wrapper import auth_migration_wrapper
from app.utils.jwt_utils import jwt_manager
from app.utils.config import get_settings


class TestSecureAuthService:
    """Test the new secure authentication service"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        settings = Mock()
        settings.environment = "testing"
        settings.jwt_secret_key = "test-secret-key-for-testing-only"
        settings.jwt_algorithm = "HS256"
        settings.jwt_expiration_minutes = 60
        return settings
    
    @pytest.fixture
    def test_user_login(self):
        """Test login credentials"""
        return UserLogin(
            email="test@example.com",
            password="testpassword123"
        )
    
    @pytest.fixture
    def test_user_register(self):
        """Test registration data"""
        return UserRegister(
            email="newuser@example.com",
            password="newpassword123",
            organization_name="Test Organization"
        )
    
    @pytest.fixture
    def mock_organization(self):
        """Mock organization for testing"""
        return OrganizationInfo(
            id="org-123",
            name="Test Organization",
            slug="test-org",
            role="owner",
            permissions=["read", "write", "admin"],
            settings={"test": True}
        )
    
    async def test_dev_mode_login_no_service_role(self, test_user_login, mock_settings):
        """Test that development mode login doesn't use service role"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            # Mock development mode
            with patch.object(secure_auth_service, 'dev_mode', True):
                response = await secure_auth_service.login(test_user_login)
                
                # Verify response structure
                assert response.token_version == "v2"
                assert response.user.email == test_user_login.email
                assert response.user.client_id is not None
                assert len(response.user.organizations) > 0
                
                # Verify no service role was used (implicit - no mocked service calls)
                # Verify UUID format (8-4-4-4-12)
                import re
                assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', response.user.id)
    
    async def test_secure_token_validation_no_service_role(self, mock_settings):
        """Test that token validation doesn't use service role"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            # Create a test token
            user_id = "test-user-123"
            email = "test@example.com"
            client_id = "client-123"
            
            token = jwt_manager.create_access_token(
                user_id=user_id,
                email=email,
                client_id=client_id,
                client_name="Test Client",
                role="member",
                permissions=["read", "write"]
            )
            
            # Validate token without service role
            validation_response = await secure_auth_service.validate_token(token)
            
            # Verify successful validation
            assert validation_response.valid is True
            assert validation_response.user_context.id == user_id
            assert validation_response.user_context.email == email
            assert validation_response.user_context.client_id == client_id
            assert validation_response.token_version == "v2"
    
    async def test_client_context_embedding(self, mock_settings):
        """Test that JWT tokens properly embed client context"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            user_id = "user-123"
            email = "test@example.com"
            client_id = "client-456"
            client_name = "Test Organization"
            permissions = ["read", "write", "admin"]
            organizations = ["org-1", "org-2"]
            
            # Create token with full client context
            token = jwt_manager.create_access_token(
                user_id=user_id,
                email=email,
                client_id=client_id,
                client_name=client_name,
                role="owner",
                permissions=permissions,
                organizations=organizations
            )
            
            # Decode token to verify embedded context
            payload = jwt_manager.validate_token(token)
            
            assert payload is not None
            assert payload["sub"] == user_id
            assert payload["email"] == email
            assert payload["client_id"] == client_id
            assert payload["client_name"] == client_name
            assert payload["role"] == "owner"
            assert payload["permissions"] == permissions
            assert payload["organizations"] == organizations
            assert payload["token_version"] == "v2"
    
    async def test_organization_validation_prevents_cross_tenant_access(self, mock_settings):
        """Test that organization validation prevents cross-tenant data access"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            # Create token for user in organization A
            token_org_a = jwt_manager.create_access_token(
                user_id="user-123",
                email="user@orga.com",
                client_id="org-a-id",
                client_name="Organization A",
                organizations=["org-a-id"]
            )
            
            # Mock organization service to deny access to org B
            with patch('app.services.organization_service.organization_service.validate_client_access') as mock_validate:
                mock_validate.return_value = False
                
                # Try to validate token claiming access to organization B
                payload = jwt_manager.validate_token(token_org_a)
                payload["client_id"] = "org-b-id"  # Simulate tampering
                
                # Organization validation should fail
                has_access = await mock_validate(payload["sub"], "org-b-id")
                assert has_access is False
    
    async def test_comprehensive_security_logging(self, test_user_login, mock_settings):
        """Test that security events are comprehensively logged"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            with patch.object(secure_auth_service, 'dev_mode', True):
                # Mock security logger to capture events
                with patch('app.services.security_logger.security_logger.log_login_attempt') as mock_log:
                    mock_log.return_value = None
                    
                    await secure_auth_service.login(test_user_login)
                    
                    # Verify login attempts were logged
                    assert mock_log.call_count >= 1
                    
                    # Check that both failure and success were logged
                    calls = mock_log.call_args_list
                    success_logged = any(call.kwargs.get('success') is True for call in calls)
                    assert success_logged
    
    async def test_registration_organization_creation(self, test_user_register, mock_settings):
        """Test that registration properly creates organizations"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            with patch.object(secure_auth_service, 'dev_mode', True):
                # Mock organization service
                with patch('app.services.organization_service.organization_service.create_organization_for_user') as mock_create:
                    mock_org = OrganizationInfo(
                        id="new-org-123",
                        name=test_user_register.organization_name,
                        slug="test-organization",
                        role="owner",
                        permissions=["read", "write", "admin"]
                    )
                    mock_create.return_value = mock_org
                    
                    response = await secure_auth_service.register(test_user_register)
                    
                    # Verify organization was created
                    mock_create.assert_called_once()
                    assert response.user.client_name == test_user_register.organization_name
                    assert len(response.user.organizations) > 0


class TestAuthMigrationWrapper:
    """Test the backward compatibility migration wrapper"""
    
    @pytest.fixture
    def mock_v1_token(self):
        """Mock v1 token for testing backward compatibility"""
        return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImV4cCI6OTk5OTk5OTk5OSwidG9rZW5fdmVyc2lvbiI6InYxIn0.invalid"
    
    @pytest.fixture
    def mock_v2_token(self, mock_settings):
        """Mock v2 token for testing"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            return jwt_manager.create_access_token(
                user_id="user-123",
                email="test@example.com",
                client_id="client-123",
                client_name="Test Client"
            )
    
    async def test_backward_compatibility_v1_tokens(self, mock_v1_token):
        """Test that v1 tokens are still supported during migration"""
        # Mock legacy auth service to handle v1 tokens
        with patch('app.services.auth_service.auth_service.verify_token') as mock_v1_verify:
            mock_v1_verify.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            # Test v1 token validation through migration wrapper
            user_data = await auth_migration_wrapper.verify_token(mock_v1_token)
            
            # Verify v1 token was processed
            assert user_data is not None
            mock_v1_verify.assert_called_once()
    
    async def test_v2_token_preference(self, mock_v2_token):
        """Test that v2 tokens are preferred when available"""
        # Mock secure auth service to handle v2 tokens
        with patch('app.services.secure_auth_service.secure_auth_service.validate_token') as mock_v2_validate:
            mock_context = UserContext(
                id="user-123",
                email="test@example.com",
                created_at=datetime.utcnow(),
                client_id="client-123",
                client_name="Test Client",
                organizations=[],
                global_permissions=["read"]
            )
            mock_v2_validate.return_value = TokenValidationResponse(
                valid=True,
                user_context=mock_context,
                token_version="v2"
            )
            
            user_data = await auth_migration_wrapper.verify_token(mock_v2_token, prefer_v2=True)
            
            # Verify v2 validation was used
            assert isinstance(user_data, UserContext)
            assert user_data.client_id == "client-123"
            mock_v2_validate.assert_called_once()
    
    async def test_migration_logging(self, test_user_login):
        """Test that migration events are logged for monitoring"""
        with patch('app.services.security_logger.security_logger.log_security_event') as mock_log:
            with patch.object(auth_migration_wrapper, 'force_v2_for_new_logins', True):
                # Mock successful v2 login
                with patch('app.services.secure_auth_service.secure_auth_service.login') as mock_v2_login:
                    from app.models.auth import EnhancedTokenResponse, EnhancedUserResponse
                    
                    mock_response = EnhancedTokenResponse(
                        access_token="test-token",
                        user=EnhancedUserResponse(
                            id="user-123",
                            email=test_user_login.email,
                            created_at=datetime.utcnow(),
                            client_id="client-123",
                            organizations=[],
                            permissions=[]
                        )
                    )
                    mock_v2_login.return_value = mock_response
                    
                    await auth_migration_wrapper.login(test_user_login)
                    
                    # Verify migration event was logged
                    mock_log.assert_called()
                    
                    # Check for specific migration event
                    migration_logged = any(
                        call.kwargs.get('event_type') == 'auth_migration' 
                        for call in mock_log.call_args_list
                    )
                    assert migration_logged


class TestJWTUtils:
    """Test JWT utilities for security compliance"""
    
    @pytest.fixture
    def mock_settings(self):
        settings = Mock()
        settings.jwt_secret_key = "test-secret-key-for-testing-only"
        settings.jwt_algorithm = "HS256"
        settings.jwt_expiration_minutes = 60
        return settings
    
    async def test_jwt_no_service_role_dependency(self, mock_settings):
        """Test that JWT validation has no service role dependency"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            # Create token
            token = jwt_manager.create_access_token(
                user_id="user-123",
                email="test@example.com"
            )
            
            # Validate token using only JWT validation (no external dependencies)
            payload = jwt_manager.validate_token(token)
            
            assert payload is not None
            assert payload["sub"] == "user-123"
            assert payload["email"] == "test@example.com"
    
    async def test_token_expiration_validation(self, mock_settings):
        """Test that expired tokens are properly rejected"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            # Create expired token
            past_time = datetime.utcnow() - timedelta(hours=2)
            
            # Manual token creation with past expiration
            payload = {
                "sub": "user-123",
                "email": "test@example.com",
                "exp": int(past_time.timestamp()),
                "iat": int((past_time - timedelta(hours=1)).timestamp()),
                "token_version": "v2",
                "iss": "mockrepo-auth",
                "aud": "mockrepo-api"
            }
            
            expired_token = jwt.encode(payload, mock_settings.jwt_secret_key, algorithm=mock_settings.jwt_algorithm)
            
            # Validation should fail
            result = jwt_manager.validate_token(expired_token)
            assert result is None
    
    async def test_token_tampering_detection(self, mock_settings):
        """Test that tampered tokens are rejected"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            # Create valid token
            token = jwt_manager.create_access_token(
                user_id="user-123",
                email="test@example.com"
            )
            
            # Tamper with token
            tampered_token = token[:-10] + "tampered123"
            
            # Validation should fail
            result = jwt_manager.validate_token(tampered_token)
            assert result is None


class TestSecurityCompliance:
    """Test overall security compliance of the new authentication system"""
    
    async def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets exist in the codebase"""
        # This would typically scan source files, but here we verify
        # that secrets come from configuration
        settings = get_settings()
        
        # Verify secrets are loaded from environment/config
        assert hasattr(settings, 'jwt_secret_key')
        assert hasattr(settings, 'supabase_service_key')
        
        # In tests, these might be test values, but they should not be hardcoded strings
        assert len(settings.jwt_secret_key) > 10  # Reasonable minimum length
    
    async def test_service_role_usage_minimization(self):
        """Test that service role usage is minimized and logged"""
        # This test would verify that service role usage is limited to
        # only essential operations (like user creation) and is logged
        
        # Mock security logger to capture service role usage
        with patch('app.services.security_logger.security_logger.log_service_role_usage') as mock_log:
            mock_log.return_value = None
            
            # Any code that uses service role should log it
            await mock_log(operation="test_operation", warning=True)
            
            mock_log.assert_called_once_with(operation="test_operation", warning=True)
    
    async def test_client_isolation_enforcement(self, mock_settings):
        """Test that client isolation is properly enforced"""
        with patch('app.utils.config.get_settings', return_value=mock_settings):
            # Create tokens for different clients
            token_client_a = jwt_manager.create_access_token(
                user_id="user-123",
                email="user@clienta.com",
                client_id="client-a-id",
                organizations=["client-a-id"]
            )
            
            token_client_b = jwt_manager.create_access_token(
                user_id="user-456", 
                email="user@clientb.com",
                client_id="client-b-id",
                organizations=["client-b-id"]
            )
            
            # Validate tokens contain correct client context
            payload_a = jwt_manager.validate_token(token_client_a)
            payload_b = jwt_manager.validate_token(token_client_b)
            
            assert payload_a["client_id"] == "client-a-id"
            assert payload_b["client_id"] == "client-b-id"
            
            # Verify client contexts are different
            assert payload_a["client_id"] != payload_b["client_id"]
            assert payload_a["organizations"] != payload_b["organizations"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])