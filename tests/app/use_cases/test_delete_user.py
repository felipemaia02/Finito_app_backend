"""Tests for use_cases/user/delete_user.py"""

import pytest
from bson import ObjectId
from app.use_cases.user.delete_user import DeleteUserUseCase


class TestDeleteUserUseCase:
    """Test cases for DeleteUserUseCase."""

    @pytest.mark.asyncio
    async def test_delete_user_success(self, mock_user_repository):
        """Test successful user deletion."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.delete.return_value = True
        use_case = DeleteUserUseCase(mock_user_repository)

        # Act
        result = await use_case.execute(user_id)

        # Assert
        assert result is True
        mock_user_repository.delete.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, mock_user_repository):
        """Test deletion when user not found."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.delete.return_value = False
        use_case = DeleteUserUseCase(mock_user_repository)

        # Act
        result = await use_case.execute(user_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_user_repository_error(self, mock_user_repository):
        """Test handling repository error during deletion."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.delete.side_effect = Exception("Database error")
        use_case = DeleteUserUseCase(mock_user_repository)

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(user_id)
