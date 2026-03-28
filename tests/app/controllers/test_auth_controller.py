"""Tests for controllers/auth_controller.py"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta

from app.controllers.auth_controller import AuthController
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.models.auth_schema import LoginRequest, RefreshTokenRequest, TokenResponse


def make_token_response():
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    return TokenResponse(
        access_token="access_token_value",
        refresh_token="refresh_token_value",
        token_type="bearer",
        expires_in=3600,
        expires_at=expires_at,
    )


class TestAuthControllerInit:
    """Test AuthController initialization."""

    def test_initialization(self):
        # Arrange & Act
        mock_repo = AsyncMock(spec=IUserRepository)
        controller = AuthController(mock_repo)

        # Assert
        assert controller is not None
        assert controller.repository == mock_repo
        assert controller.login_use_case is not None
        assert controller.refresh_token_use_case is not None


class TestAuthControllerLogin:
    """Test AuthController.login delegation."""

    @pytest.mark.asyncio
    async def test_login_delegates_to_use_case(self):
        # Arrange
        mock_repo = AsyncMock(spec=IUserRepository)
        controller = AuthController(mock_repo)
        token_response = make_token_response()
        login_data = LoginRequest(email="user@example.com", password="pass123")

        with patch.object(
            controller.login_use_case, "execute", AsyncMock(return_value=token_response)
        ) as mock_exec:
            # Act
            result = await controller.login(login_data)

        # Assert
        assert result == token_response
        mock_exec.assert_called_once_with(login_data)

    @pytest.mark.asyncio
    async def test_login_propagates_exception(self):
        # Arrange
        mock_repo = AsyncMock(spec=IUserRepository)
        controller = AuthController(mock_repo)
        login_data = LoginRequest(email="user@example.com", password="wrong")

        with patch.object(
            controller.login_use_case,
            "execute",
            AsyncMock(side_effect=Exception("Auth error")),
        ):
            # Act & Assert
            with pytest.raises(Exception, match="Auth error"):
                await controller.login(login_data)


class TestAuthControllerRefreshToken:
    """Test AuthController.refresh_token delegation."""

    @pytest.mark.asyncio
    async def test_refresh_token_delegates_to_use_case(self):
        # Arrange
        mock_repo = AsyncMock(spec=IUserRepository)
        controller = AuthController(mock_repo)
        token_response = make_token_response()
        refresh_data = RefreshTokenRequest(refresh_token="valid_refresh_token")

        with patch.object(
            controller.refresh_token_use_case,
            "execute",
            AsyncMock(return_value=token_response),
        ) as mock_exec:
            # Act
            result = await controller.refresh_token(refresh_data)

        # Assert
        assert result == token_response
        mock_exec.assert_called_once_with(refresh_data.refresh_token)

    @pytest.mark.asyncio
    async def test_refresh_token_propagates_value_error(self):
        # Arrange
        mock_repo = AsyncMock(spec=IUserRepository)
        controller = AuthController(mock_repo)
        refresh_data = RefreshTokenRequest(refresh_token="expired_token")

        with patch.object(
            controller.refresh_token_use_case,
            "execute",
            AsyncMock(side_effect=ValueError("Invalid token")),
        ):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid token"):
                await controller.refresh_token(refresh_data)

    @pytest.mark.asyncio
    async def test_refresh_token_propagates_generic_exception(self):
        # Arrange
        mock_repo = AsyncMock(spec=IUserRepository)
        controller = AuthController(mock_repo)
        refresh_data = RefreshTokenRequest(refresh_token="some_token")

        with patch.object(
            controller.refresh_token_use_case,
            "execute",
            AsyncMock(side_effect=Exception("Unexpected")),
        ):
            # Act & Assert
            with pytest.raises(Exception, match="Unexpected"):
                await controller.refresh_token(refresh_data)
