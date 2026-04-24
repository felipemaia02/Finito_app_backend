"""Tests for controllers/user_controller.py"""

import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from app.controllers.user_controller import UserController
from app.models.user_schema import UserUpdate
from app.models.email_verification_schema import UserRegisterResponse


def make_controller(mock_user_repository, mock_verification_repository, mock_email_service):
    return UserController(mock_user_repository, mock_verification_repository, mock_email_service)


class TestUserController:
    """Test cases for UserController."""

    def test_controller_initialization(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        """Test controller initialization."""
        controller = make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )
        assert controller.repository is not None
        assert controller.create_user_use_case is not None
        assert controller.send_verification_use_case is not None
        assert controller.get_user_by_id_use_case is not None
        assert controller.get_all_users_use_case is not None
        assert controller.get_user_by_email_use_case is not None
        assert controller.update_user_use_case is not None
        assert controller.delete_user_use_case is not None

    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        sample_user_create,
        sample_user_response,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        """Test successful user registration."""
        # Arrange
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.create.return_value = sample_user_response
        mock_verification_repository.get_latest_by_user_id.return_value = None
        mock_verification_repository.invalidate_all_by_user_id.return_value = None
        mock_verification_repository.create.return_value = None
        mock_email_service.send_verification_email.return_value = None
        controller = make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        result = await controller.register_user(sample_user_create)

        # Assert
        assert result is not None
        assert isinstance(result, UserRegisterResponse)
        assert "registered" in result.message.lower()
        assert result.verification_token != ""

    @pytest.mark.asyncio
    async def test_get_user_success(
        self,
        sample_user_response,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        """Test getting user by ID."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.get_by_id.return_value = sample_user_response
        controller = make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        result = await controller.get_user(user_id)

        # Assert
        assert result is not None
        assert result.email == sample_user_response.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self,
        sample_user_response,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        """Test getting user by email."""
        # Arrange
        email = "john@example.com"
        mock_user_repository.get_by_email.return_value = sample_user_response
        controller = make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        result = await controller.get_user_by_email(email)

        # Assert
        assert result is not None
        assert result.email == email

    @pytest.mark.asyncio
    async def test_get_all_users_success(
        self,
        sample_user_response,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        """Test getting all users."""
        # Arrange
        users_list = [sample_user_response]
        mock_user_repository.get_all.return_value = users_list
        controller = make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        result = await controller.get_all_users(skip=0, limit=100)

        # Assert
        assert len(result) == 1
        assert result[0].email == sample_user_response.email

    @pytest.mark.asyncio
    async def test_update_user_success(
        self,
        sample_user_entity,
        sample_user_response,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        """Test user update."""
        # Arrange
        user_id = str(ObjectId())
        update_data = UserUpdate(name="Updated Name")

        mock_user_repository.get_by_id.return_value = sample_user_entity
        mock_user_repository.email_exists.return_value = False
        mock_user_repository.update.return_value = sample_user_entity
        controller = make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        result = await controller.update_user(user_id, update_data)

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        """Test user deletion."""
        # Arrange
        user_id = str(ObjectId())
        mock_user_repository.delete.return_value = True
        controller = make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        result = await controller.delete_user(user_id)

        # Assert
        assert result is True

