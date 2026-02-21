"""Tests for use_cases/user/update_user.py"""

import pytest
from datetime import date
from bson import ObjectId
from app.use_cases.user.update_user import UpdateUserUseCase
from app.models.user_schema import UserUpdate
from app.domain.dtos.user_dtos import UpdateUserInput


class TestUpdateUserUseCase:
    """Test cases for UpdateUserUseCase."""
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, sample_user_entity, mock_user_repository):
        """Test successful user update."""
        # Arrange
        user_id = str(ObjectId())
        update_data = UserUpdate(name="Updated Name")
        input_data = UpdateUserInput(user_id=user_id, user_data=update_data)
        
        updated_user = sample_user_entity
        updated_user.name = "Updated Name"
        
        mock_user_repository.get_by_id.return_value = sample_user_entity
        mock_user_repository.email_exists.return_value = False
        mock_user_repository.update.return_value = updated_user
        
        use_case = UpdateUserUseCase(mock_user_repository)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result is not None
        assert result.name == "Updated Name"
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, mock_user_repository):
        """Test update when user not found."""
        # Arrange
        user_id = str(ObjectId())
        update_data = UserUpdate(name="Updated Name")
        input_data = UpdateUserInput(user_id=user_id, user_data=update_data)
        
        mock_user_repository.get_by_id.return_value = None
        use_case = UpdateUserUseCase(mock_user_repository)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result is None
        mock_user_repository.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_user_with_existing_email(self, sample_user_entity, mock_user_repository):
        """Test update with email that already exists."""
        # Arrange
        from copy import deepcopy
        user_id = str(ObjectId())
        update_data = UserUpdate(email="existing@example.com")
        input_data = UpdateUserInput(user_id=user_id, user_data=update_data)
        
        # Create a clean copy of the sample user entity for get_by_id
        get_by_id_user = deepcopy(sample_user_entity)
        mock_user_repository.get_by_id.return_value = get_by_id_user
        
        # Create another user with the conflicting email
        conflicting_user = deepcopy(sample_user_entity)
        conflicting_user.email = "existing@example.com"
        mock_user_repository.get_by_email.return_value = conflicting_user
        
        use_case = UpdateUserUseCase(mock_user_repository)
        
        # Act & Assert
        with pytest.raises(ValueError, match="is already registered"):
            await use_case.execute(input_data)
    
    @pytest.mark.asyncio
    async def test_update_user_email_normalized_to_lowercase(self, sample_user_entity, mock_user_repository):
        """Test that email is normalized to lowercase during update."""
        # Arrange
        user_id = str(ObjectId())
        update_data = UserUpdate(email="TEST@EXAMPLE.COM")
        input_data = UpdateUserInput(user_id=user_id, user_data=update_data)
        
        mock_user_repository.get_by_id.return_value = sample_user_entity
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.update.return_value = sample_user_entity
        
        use_case = UpdateUserUseCase(mock_user_repository)
        
        # Act
        await use_case.execute(input_data)
        
        # Assert
        call_args = mock_user_repository.update.call_args[0][1]
        assert call_args.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_update_user_partial_update(self, sample_user_entity, mock_user_repository):
        """Test partial user update (only some fields)."""
        # Arrange
        user_id = str(ObjectId())
        update_data = UserUpdate(name="New Name")  # Only update name
        input_data = UpdateUserInput(user_id=user_id, user_data=update_data)
        
        original_email = sample_user_entity.email
        
        mock_user_repository.get_by_id.return_value = sample_user_entity
        mock_user_repository.update.return_value = sample_user_entity
        
        use_case = UpdateUserUseCase(mock_user_repository)
        
        # Act
        await use_case.execute(input_data)
        
        # Assert
        call_args = mock_user_repository.update.call_args[0][1]
        assert call_args.name == "New Name"
        assert call_args.email == original_email  # Email should remain unchanged
