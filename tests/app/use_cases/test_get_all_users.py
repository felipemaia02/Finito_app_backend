"""Tests for use_cases/user/get_all_users.py"""

import pytest
from app.use_cases.user.get_all_users import GetAllUsersUseCase
from app.domain.dtos.user_dtos import GetAllUsersInput


class TestGetAllUsersUseCase:
    """Test cases for GetAllUsersUseCase."""
    
    @pytest.mark.asyncio
    async def test_get_all_users_success(self, sample_user_entity, mock_user_repository):
        """Test successful retrieval of all users."""
        # Arrange
        users_list = [sample_user_entity]
        mock_user_repository.get_all.return_value = users_list
        use_case = GetAllUsersUseCase(mock_user_repository)
        input_data = GetAllUsersInput(skip=0, limit=100)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert len(result) == 1
        assert result[0].email == sample_user_entity.email
        mock_user_repository.get_all.assert_called_once_with(skip=0, limit=100)
    
    @pytest.mark.asyncio
    async def test_get_all_users_empty(self, mock_user_repository):
        """Test retrieval when no users exist."""
        # Arrange
        mock_user_repository.get_all.return_value = []
        use_case = GetAllUsersUseCase(mock_user_repository)
        input_data = GetAllUsersInput(skip=0, limit=100)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_all_users_with_pagination(self, sample_user_entity, mock_user_repository):
        """Test pagination parameters are passed correctly."""
        # Arrange
        users_list = [sample_user_entity]
        mock_user_repository.get_all.return_value = users_list
        use_case = GetAllUsersUseCase(mock_user_repository)
        input_data = GetAllUsersInput(skip=10, limit=50)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        mock_user_repository.get_all.assert_called_once_with(skip=10, limit=50)
        assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_get_all_users_repository_error(self, mock_user_repository):
        """Test handling repository error."""
        # Arrange
        mock_user_repository.get_all.side_effect = Exception("Database error")
        use_case = GetAllUsersUseCase(mock_user_repository)
        input_data = GetAllUsersInput(skip=0, limit=100)
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(input_data)
