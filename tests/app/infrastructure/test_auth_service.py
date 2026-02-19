"""Tests for authentication service."""

import pytest
from app.infrastructure.services.auth_service import APIKeyAuthService
from app.infrastructure.settings import get_settings


@pytest.fixture
def auth_service():
    """Provide an authentication service instance."""
    return APIKeyAuthService()


class TestAuthService:
    """Test cases for API Key authentication service."""
    
    @pytest.mark.asyncio
    async def test_validate_api_key_valid(self, auth_service):
        """Test validation with valid API key."""
        # Arrange
        settings = get_settings()
        valid_key = settings.api_key
        
        # Act
        result = await auth_service.validate_api_key(valid_key)
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_api_key_invalid(self, auth_service):
        """Test validation with invalid API key."""
        # Arrange
        invalid_key = "wrong-key"
        
        # Act
        result = await auth_service.validate_api_key(invalid_key)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_api_key_empty(self, auth_service):
        """Test validation with empty API key."""
        # Arrange
        empty_key = ""
        
        # Act
        result = await auth_service.validate_api_key(empty_key)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_api_key_wrong_format(self, auth_service):
        """Test validation with wrong format."""
        # Arrange
        settings = get_settings()
        wrong_format = settings.api_key + "extra"
        
        # Act
        result = await auth_service.validate_api_key(wrong_format)
        
        # Assert
        assert result is False
    
    def test_auth_service_can_be_instantiated(self):
        """Test that auth service can be instantiated."""
        # Act
        service = APIKeyAuthService()
        
        # Assert
        assert service is not None
    
    def test_auth_service_has_settings(self, auth_service):
        """Test that auth service has access to settings."""
        # Assert
        assert auth_service.settings is not None
        assert hasattr(auth_service.settings, 'api_key')
