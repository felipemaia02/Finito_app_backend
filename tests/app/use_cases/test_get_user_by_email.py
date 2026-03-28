"""Tests for use_cases/user/get_user_by_email.py"""

import pytest
from app.use_cases.user.get_user_by_email import GetUserByEmailUseCase
from app.domain.dtos.user_dtos import GetUserByEmailInput


class TestGetUserByEmailUseCase:
    """Test cases for GetUserByEmailUseCase."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self, sample_user_entity, mock_user_repository
    ):
        """Test successful retrieval of user by email."""
        # Arrange
        email = "john@example.com"
        mock_user_repository.get_by_email.return_value = sample_user_entity
        use_case = GetUserByEmailUseCase(mock_user_repository)
        input_data = GetUserByEmailInput(email=email)

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is not None
        assert result.email == email
        mock_user_repository.get_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, mock_user_repository):
        """Test retrieval when user email not found."""
        # Arrange
        email = "nonexistent@example.com"
        mock_user_repository.get_by_email.return_value = None
        use_case = GetUserByEmailUseCase(mock_user_repository)
        input_data = GetUserByEmailInput(email=email)

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_repository_error(self, mock_user_repository):
        """Test handling repository error."""
        # Arrange
        email = "test@example.com"
        mock_user_repository.get_by_email.side_effect = Exception("Database error")
        use_case = GetUserByEmailUseCase(mock_user_repository)
        input_data = GetUserByEmailInput(email=email)

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(input_data)
