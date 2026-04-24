"""Tests for use_cases/auth/refresh_token.py"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta

from app.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.models.auth_schema import TokenData


class TestRefreshTokenUseCase:
    """Test cases for RefreshTokenUseCase."""

    def test_initialization(self):
        """Test use case can be instantiated."""
        use_case = RefreshTokenUseCase()
        assert use_case is not None
        assert use_case.oauth_service is not None

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful token refresh."""
        use_case = RefreshTokenUseCase()

        # Use naive datetime and int timestamp as expected by TokenData
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        exp_timestamp = int(expires_at.timestamp())
        token_data = TokenData(sub="test@example.com", exp=exp_timestamp)
        access_token = "new_access_token"
        refresh_token = "new_refresh_token"

        with patch.object(
            use_case.oauth_service, "verify_token", return_value=token_data
        ), patch.object(
            use_case.oauth_service,
            "create_token_pair",
            return_value=(access_token, refresh_token, expires_at),
        ):
            result = await use_case.execute("valid_refresh_token")

        assert result is not None
        assert result.access_token == access_token
        assert result.refresh_token == refresh_token
        assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_execute_invalid_token(self):
        """Test refresh with invalid token raises ValueError."""
        use_case = RefreshTokenUseCase()

        with patch.object(use_case.oauth_service, "verify_token", return_value=None):
            with pytest.raises(ValueError, match="Invalid or expired refresh token"):
                await use_case.execute("invalid_token")

    @pytest.mark.asyncio
    async def test_execute_raises_value_error_from_service(self):
        """Test that ValueError from service is re-raised."""
        use_case = RefreshTokenUseCase()

        with patch.object(
            use_case.oauth_service,
            "verify_token",
            side_effect=ValueError("Token expired"),
        ):
            with pytest.raises(ValueError):
                await use_case.execute("expired_token")

    @pytest.mark.asyncio
    async def test_execute_raises_generic_exception(self):
        """Test that unexpected Exception is re-raised."""
        use_case = RefreshTokenUseCase()

        with patch.object(
            use_case.oauth_service,
            "verify_token",
            side_effect=Exception("Unexpected error"),
        ):
            with pytest.raises(Exception, match="Unexpected error"):
                await use_case.execute("some_token")

    @pytest.mark.asyncio
    async def test_execute_returns_token_response_with_expires_in(self):
        """Test returned token response has positive expires_in."""
        use_case = RefreshTokenUseCase()

        # Use naive datetime and int timestamp as expected by TokenData
        expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
        exp_timestamp = int(expires_at.timestamp())
        token_data = TokenData(sub="user@example.com", exp=exp_timestamp)

        with patch.object(
            use_case.oauth_service, "verify_token", return_value=token_data
        ), patch.object(
            use_case.oauth_service,
            "create_token_pair",
            return_value=("access", "refresh", expires_at),
        ):
            result = await use_case.execute("valid_token")

        assert result.expires_in > 0
        assert result.expires_at == expires_at
