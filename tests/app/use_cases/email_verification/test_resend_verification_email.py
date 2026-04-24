"""Tests for use_cases/email_verification/resend_verification_email.py"""

import pytest
from unittest.mock import AsyncMock, patch

from app.use_cases.email_verification.resend_verification_email import (
    ResendVerificationEmailUseCase,
)
from app.domain.dtos.email_verification_dtos import ResendVerificationEmailInput


class TestResendVerificationEmailUseCase:
    """Tests for ResendVerificationEmailUseCase."""

    def _make_use_case(
        self, mock_user_repository, mock_verification_repository, mock_email_service
    ):
        return ResendVerificationEmailUseCase(
            user_repository=mock_user_repository,
            verification_repository=mock_verification_repository,
            email_service=mock_email_service,
        )

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_resend_success(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
        sample_unverified_user_entity,
        sample_verification_token_entity,
    ):
        # Arrange
        sample_verification_token_entity.resend_count = 1
        mock_user_repository.get_by_id_unverified.return_value = (
            sample_unverified_user_entity
        )
        mock_verification_repository.get_latest_by_user_id.return_value = (
            sample_verification_token_entity
        )

        input_data = ResendVerificationEmailInput(
            user_id=sample_unverified_user_entity.id
        )
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act — patch SendVerificationEmailUseCase to avoid deep integration
        with patch(
            "app.use_cases.email_verification.resend_verification_email.SendVerificationEmailUseCase"
        ) as MockSend:
            MockSend.return_value.execute = AsyncMock(return_value="new-jwt-token")
            result = await use_case.execute(input_data)

        # Assert
        assert result.message == "Verification email sent. Please check your inbox."
        MockSend.return_value.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_resend_success_no_previous_token(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
        sample_unverified_user_entity,
    ):
        # Arrange — no previous token at all
        mock_user_repository.get_by_id_unverified.return_value = (
            sample_unverified_user_entity
        )
        mock_verification_repository.get_latest_by_user_id.return_value = None

        input_data = ResendVerificationEmailInput(
            user_id=sample_unverified_user_entity.id
        )
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act
        with patch(
            "app.use_cases.email_verification.resend_verification_email.SendVerificationEmailUseCase"
        ) as MockSend:
            MockSend.return_value.execute = AsyncMock(return_value="jwt-token")
            result = await use_case.execute(input_data)

        # Assert
        assert "inbox" in result.message.lower()

    # ------------------------------------------------------------------
    # Failure cases
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_raises_when_user_not_found(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange
        mock_user_repository.get_by_id_unverified.return_value = None
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            await use_case.execute(ResendVerificationEmailInput(user_id="nonexistent"))

        mock_verification_repository.get_latest_by_user_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_when_email_already_verified(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
        sample_unverified_user_entity,
    ):
        # Arrange — user already verified
        sample_unverified_user_entity.is_email_verified = True
        mock_user_repository.get_by_id_unverified.return_value = (
            sample_unverified_user_entity
        )
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act & Assert
        with pytest.raises(ValueError, match="already verified"):
            await use_case.execute(
                ResendVerificationEmailInput(user_id=sample_unverified_user_entity.id)
            )

        mock_verification_repository.get_latest_by_user_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_when_resend_limit_reached(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
        sample_unverified_user_entity,
        sample_verification_token_entity,
    ):
        # Arrange — resend_count at limit
        sample_verification_token_entity.resend_count = 3
        mock_user_repository.get_by_id_unverified.return_value = (
            sample_unverified_user_entity
        )
        mock_verification_repository.get_latest_by_user_id.return_value = (
            sample_verification_token_entity
        )
        use_case = self._make_use_case(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum number"):
            await use_case.execute(
                ResendVerificationEmailInput(user_id=sample_unverified_user_entity.id)
            )
