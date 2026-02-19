"""Tests for use_cases/user/get_user_by_id.py"""

import pytest
from bson import ObjectId
from app.use_cases.user.get_user_by_id import GetUserByIdUseCase


class TestGetUserByIdUseCase:
    """Test cases for GetUserByIdUseCase."""
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, sample_user_entity, mock_user_repository):
        """Test successful retrieval of user by ID."""
        # Arrange
        user_id = str(ObjectId())
        sample_user_entity.id = user_id
        mock_user_repository.get_by_id.return_value = sample_user_entity
        use_case = GetUserByIdUseCase(mock_user_repository)
        
        # Act
        result = await use_case.execute(user_id)
        
        # Assert
        assert result is not None
        assert result.id == user_id
        assert result.email == sample_user_entity.email
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_user_repository):
        """Test retrieval when user not found."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.get_by_id.return_value = None
        use_case = GetUserByIdUseCase(mock_user_repository)
        
        # Act
        result = await use_case.execute(user_id)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_repository_error(self, mock_user_repository):
        """Test handling repository error."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.get_by_id.side_effect = Exception("Database error")
        use_case = GetUserByIdUseCase(mock_user_repository)
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(user_id)
