"""Tests for use_cases/auth/login.py"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, date
from fastapi import HTTPException, status

from app.use_cases.auth.login import LoginUseCase
from app.models.auth_schema import LoginRequest
from app.domain.entities.user_entity import User


class TestLoginUseCase:
    """Test cases for LoginUseCase."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, mock_user_repository):
        """Test successful user login."""
        # Arrange
        login_data = LoginRequest(
            email="john@example.com",
            password="password123"
        )
        
        user = User(
            id="507f1f77bcf86cd799439011",
            name="John Silva",
            email="john@example.com",
            password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyB2x8z9RZMK",  # hashed "password123"
            date_birth=date(1990, 5, 15),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        mock_user_repository.get_by_email.return_value = user
        use_case = LoginUseCase(mock_user_repository)
        
        # Act
        with patch('app.use_cases.auth.login.verify_password', return_value=True):
            result = await use_case.execute(login_data)
        
        # Assert
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
        assert result.expires_in > 0
        mock_user_repository.get_by_email.assert_called_once_with(login_data.email)
    
    @pytest.mark.asyncio
    async def test_login_user_not_found(self, mock_user_repository):
        """Test login with non-existent user."""
        # Arrange
        login_data = LoginRequest(
            email="nonexistent@example.com",
            password="password123"
        )
        
        mock_user_repository.get_by_email.return_value = None
        use_case = LoginUseCase(mock_user_repository)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await use_case.execute(login_data)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid email or password"
        mock_user_repository.get_by_email.assert_called_once_with(login_data.email)
    
    @pytest.mark.asyncio
    async def test_login_incorrect_password(self, mock_user_repository):
        """Test login with incorrect password."""
        # Arrange
        login_data = LoginRequest(
            email="john@example.com",
            password="wrongpassword"
        )
        
        user = User(
            id="507f1f77bcf86cd799439011",
            name="John Silva",
            email="john@example.com",
            password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyB2x8z9RZMK",  # hashed "password123"
            date_birth=date(1990, 5, 15),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        mock_user_repository.get_by_email.return_value = user
        use_case = LoginUseCase(mock_user_repository)
        
        # Act & Assert
        with patch('app.use_cases.auth.login.verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await use_case.execute(login_data)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid email or password"
        mock_user_repository.get_by_email.assert_called_once_with(login_data.email)
    
    @pytest.mark.asyncio
    async def test_login_email_case_insensitive(self, mock_user_repository):
        """Test that login handles email case properly."""
        # Arrange
        login_data = LoginRequest(
            email="JOHN@EXAMPLE.COM",
            password="password123"
        )
        
        user = User(
            id="507f1f77bcf86cd799439011",
            name="John Silva",
            email="john@example.com",
            password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyB2x8z9RZMK",
            date_birth=date(1990, 5, 15),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        mock_user_repository.get_by_email.return_value = user
        use_case = LoginUseCase(mock_user_repository)
        
        # Act
        with patch('app.use_cases.auth.login.verify_password', return_value=True):
            result = await use_case.execute(login_data)
        
        # Assert
        assert result.access_token is not None
        mock_user_repository.get_by_email.assert_called_once_with(login_data.email)
    
    @pytest.mark.asyncio
    async def test_login_repository_error(self, mock_user_repository):
        """Test handling repository error during login."""
        # Arrange
        login_data = LoginRequest(
            email="john@example.com",
            password="password123"
        )
        
        mock_user_repository.get_by_email.side_effect = Exception("Database error")
        use_case = LoginUseCase(mock_user_repository)
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(login_data)
