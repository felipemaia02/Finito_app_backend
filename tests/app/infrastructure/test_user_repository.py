"""Tests for infrastructure/repositories/user_repository.py"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import date
from bson import ObjectId
from app.infrastructure.repositories.user_repository import MongoUserRepository
from app.domain.entities.user_entity import User


class TestMongoUserRepository:
    """Test cases for MongoUserRepository."""
    
    def test_repository_initialization(self):
        """Test repository initialization."""
        repo = MongoUserRepository()
        assert repo.collection_name == "users"
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, sample_user_entity, mock_user_repository):
        """Test successful user creation."""
        # Arrange
        sample_user_entity.id = str(ObjectId())
        mock_user_repository.create.return_value = sample_user_entity
        
        # Act
        result = await mock_user_repository.create(sample_user_entity)
        
        # Assert
        assert result.id == sample_user_entity.id
        assert result.email == sample_user_entity.email
        mock_user_repository.create.assert_called_once_with(sample_user_entity)
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, mock_user_repository, sample_user_entity):
        """Test that duplicate email raises error."""
        # Arrange
        mock_user_repository.create.side_effect = ValueError("Email is already registered")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email is already registered"):
            await mock_user_repository.create(sample_user_entity)
    
    @pytest.mark.asyncio
    async def test_get_by_id_success(self, sample_user_entity, mock_user_repository):
        """Test getting user by ID."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.get_by_id.return_value = sample_user_entity
        
        # Act
        result = await mock_user_repository.get_by_id(user_id)
        
        # Assert
        assert result is not None
        assert result.id == sample_user_entity.id
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_user_repository):
        """Test getting user by ID when not found."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.get_by_id.return_value = None
        
        # Act
        result = await mock_user_repository.get_by_id(user_id)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_email_success(self, sample_user_entity, mock_user_repository):
        """Test getting user by email."""
        # Arrange
        email = "joao@example.com"
        mock_user_repository.get_by_email.return_value = sample_user_entity
        
        # Act
        result = await mock_user_repository.get_by_email(email)
        
        # Assert
        assert result is not None
        assert result.email == email
        mock_user_repository.get_by_email.assert_called_once_with(email)
    
    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, mock_user_repository):
        """Test getting user by email when not found."""
        # Arrange
        email = "nonexistent@example.com"
        mock_user_repository.get_by_email.return_value = None
        
        # Act
        result = await mock_user_repository.get_by_email(email)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_email_exists_true(self, mock_user_repository):
        """Test email_exists returns True when email is registered."""
        # Arrange
        email = "joao@example.com"
        mock_user_repository.email_exists.return_value = True
        
        # Act
        result = await mock_user_repository.email_exists(email)
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_email_exists_false(self, mock_user_repository):
        """Test email_exists returns False when email is not registered."""
        # Arrange
        email = "nonexistent@example.com"
        mock_user_repository.email_exists.return_value = False
        
        # Act
        result = await mock_user_repository.email_exists(email)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_all_success(self, sample_user_entity, mock_user_repository):
        """Test getting all users with pagination."""
        # Arrange
        users_list = [sample_user_entity]
        mock_user_repository.get_all.return_value = users_list
        
        # Act
        result = await mock_user_repository.get_all(skip=0, limit=100)
        
        # Assert
        assert len(result) == 1
        assert result[0].email == sample_user_entity.email
        mock_user_repository.get_all.assert_called_once_with(skip=0, limit=100)
    
    @pytest.mark.asyncio
    async def test_get_all_empty(self, mock_user_repository):
        """Test getting all users when list is empty."""
        # Arrange
        mock_user_repository.get_all.return_value = []
        
        # Act
        result = await mock_user_repository.get_all(skip=0, limit=100)
        
        # Assert
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_update_success(self, sample_user_entity, mock_user_repository):
        """Test successful user update."""
        # Arrange
        user_id = str(ObjectId())
        updated_user = sample_user_entity
        updated_user.nome = "Updated Name"
        mock_user_repository.update.return_value = updated_user
        
        # Act
        result = await mock_user_repository.update(user_id, updated_user)
        
        # Assert
        assert result.nome == "Updated Name"
        mock_user_repository.update.assert_called_once_with(user_id, updated_user)
    
    @pytest.mark.asyncio
    async def test_update_not_found(self, mock_user_repository, sample_user_entity):
        """Test update when user not found."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.update.return_value = None
        
        # Act
        result = await mock_user_repository.update(user_id, sample_user_entity)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_success(self, mock_user_repository):
        """Test successful user deletion (soft delete)."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.delete.return_value = True
        
        # Act
        result = await mock_user_repository.delete(user_id)
        
        # Assert
        assert result is True
        mock_user_repository.delete.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_user_repository):
        """Test delete when user not found."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.delete.return_value = False
        
        # Act
        result = await mock_user_repository.delete(user_id)
        
        # Assert
        assert result is False
