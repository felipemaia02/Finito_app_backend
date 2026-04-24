"""Tests for use_cases/email_verification/request_verification_email.py"""

import pytest
from unittest.mock import AsyncMock, patch

from app.use_cases.email_verification.request_verification_email import (
    RequestVerificationEmailUseCase,
)
from app.domain.dtos.email_verification_dtos import RequestVerificationInput

_GENERIC_MSG = "If this email is registered and unverified, a code has been sent."


class TestRequestVerificationEmailUseCase:
    """Tests for RequestVerificationEmailUseCase (opaque response pattern)."""

    def _make_use_case(
        self, mock_user_repository, mock_verification_repository, mock_email_service
    ):
        return RequestVerificationEmailUseCase(
            user_repository=mock_user_repository,
            verification_repository=mock_verification_repository,
            email_service=mock_email_service,
        )

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_returns_token_when_valid_unverified_user(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
        sample_unverified_user_entity,
    ):
        # Arrange
        mock_user_repository.get_by_email_unverified.return_value = (
            sample_unverified_user_entity
        )
        input_data = RequestVerificationInput(email="maria@example.com")
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        with patch(
            "app.use_cases.email_verification.request_verification_email.SendVerificationEmailUseCase"
        ) as MockSend:
            MockSend.return_value.execute = AsyncMock(return_value="new-jwt")
            result = await use_case.execute(input_data)

        # Assert
        assert result.verification_token == "new-jwt"
        assert result.message == _GENERIC_MSG
        MockSend.return_value.execute.assert_called_once()

    # ------------------------------------------------------------------
    # Opaque-response cases (all return generic message, no exception)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_returns_generic_response_when_email_not_found(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange — email does not exist
        mock_user_repository.get_by_email_unverified.return_value = None
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        result = await use_case.execute(
            RequestVerificationInput(email="ghost@example.com")
        )

        # Assert — same message, empty token, no exception raised
        assert result.message == _GENERIC_MSG
        assert result.verification_token == ""

    @pytest.mark.asyncio
    async def test_returns_generic_response_when_already_verified(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
        sample_unverified_user_entity,
    ):
        # Arrange — user already verified
        sample_unverified_user_entity.is_email_verified = True
        mock_user_repository.get_by_email_unverified.return_value = (
            sample_unverified_user_entity
        )
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        result = await use_case.execute(
            RequestVerificationInput(email="maria@example.com")
        )

        # Assert — generic, no token
        assert result.message == _GENERIC_MSG
        assert result.verification_token == ""

    @pytest.mark.asyncio
    async def test_returns_generic_response_when_resend_limit_reached(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
        sample_unverified_user_entity,
    ):
        # Arrange — SendVerificationEmailUseCase raises ValueError (limit)
        mock_user_repository.get_by_email_unverified.return_value = (
            sample_unverified_user_entity
        )
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        with patch(
            "app.use_cases.email_verification.request_verification_email.SendVerificationEmailUseCase"
        ) as MockSend:
            MockSend.return_value.execute = AsyncMock(
                side_effect=ValueError("Maximum number of verification email resends reached.")
            )
            result = await use_case.execute(
                RequestVerificationInput(email="maria@example.com")
            )

        # Assert — attacker gets no useful signal
        assert result.message == _GENERIC_MSG
        assert result.verification_token == ""

    @pytest.mark.asyncio
    async def test_propagates_infrastructure_exception(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange — DB throws unexpected error
        mock_user_repository.get_by_email_unverified.side_effect = Exception(
            "DB connection lost"
        )
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act & Assert — infrastructure errors ARE propagated
        with pytest.raises(Exception, match="DB connection lost"):
            await use_case.execute(
                RequestVerificationInput(email="maria@example.com")
            )
