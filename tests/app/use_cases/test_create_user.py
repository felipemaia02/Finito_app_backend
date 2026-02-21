"""Tests for use_cases/user/create_user.py"""

import pytest
from datetime import date
from unittest.mock import AsyncMock
from app.use_cases.user.create_user import CreateUserUseCase
from app.models.user_schema import UserCreate


class TestCreateUserUseCase:
    """Test cases for CreateUserUseCase."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, sample_user_create, sample_user_response, mock_user_repository):
        """Test successful user creation."""
        # Arrange
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.create.return_value = sample_user_response
        use_case = CreateUserUseCase(mock_user_repository)
        
        # Act
        result = await use_case.execute(sample_user_create)
        
        # Assert
        assert result.name == sample_user_response.name
        assert result.email == sample_user_response.email
        mock_user_repository.get_by_email.assert_called_once()
        mock_user_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_email_already_exists(self, sample_user_create, sample_user_entity, mock_user_repository):
        """Test that creating user with existing email raises error."""
        # Arrange
        mock_user_repository.get_by_email.return_value = sample_user_entity
        use_case = CreateUserUseCase(mock_user_repository)
        
        # Act & Assert
        with pytest.raises(ValueError, match="is already registered"):
            await use_case.execute(sample_user_create)
        
        mock_user_repository.get_by_email.assert_called_once()
        mock_user_repository.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_user_email_normalized_to_lowercase(self, mock_user_repository, sample_user_response):
        """Test that email is normalized to lowercase."""
        # Arrange
        user_create = UserCreate(
            name="Test User",
            email="TEST@EXAMPLE.COM",
            password="password123!",
            date_birth=date(1990, 1, 1),
        )
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.create.return_value = sample_user_response
        use_case = CreateUserUseCase(mock_user_repository)
        
        # Act
        await use_case.execute(user_create)
        
        # Assert
        call_args = mock_user_repository.create.call_args[0][0]
        assert call_args.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_create_user_password_is_hashed(self, mock_user_repository, sample_user_response):
        """Test that password is hashed, not stored as plain text."""
        # Arrange
        user_create = UserCreate(
            name="Test User",
            email="test@example.com",
            password="plain_password",
            date_birth=date(1990, 1, 1),
        )
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.create.return_value = sample_user_response
        use_case = CreateUserUseCase(mock_user_repository)
        
        # Act
        await use_case.execute(user_create)
        
        # Assert
        call_args = mock_user_repository.create.call_args[0][0]
        # Password should be hashed (starts with $2b$ for bcrypt)
        assert call_args.password.startswith("$2b$")
        assert call_args.password != "plain_password"
    
    @pytest.mark.asyncio
    async def test_create_user_repository_error(self, sample_user_create, mock_user_repository):
        """Test handling repository error during creation."""
        # Arrange
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.create.side_effect = Exception("Database error")
        use_case = CreateUserUseCase(mock_user_repository)
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(sample_user_create)
