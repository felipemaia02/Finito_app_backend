"""Tests for use_cases/email_verification/send_verification_email.py"""

import hashlib
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from app.use_cases.email_verification.send_verification_email import (
    SendVerificationEmailUseCase,
)
from app.domain.dtos.email_verification_dtos import SendVerificationEmailInput
from app.domain.entities.email_verification_token_entity import EmailVerificationToken


class TestSendVerificationEmailUseCase:
    """Tests for SendVerificationEmailUseCase."""

    def _make_use_case(self, mock_verification_repository, mock_email_service):
        return SendVerificationEmailUseCase(
            verification_repository=mock_verification_repository,
            email_service=mock_email_service,
        )

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_send_success_first_time(
        self,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange
        mock_verification_repository.get_latest_by_user_id.return_value = None
        mock_verification_repository.invalidate_all_by_user_id.return_value = None
        mock_verification_repository.create.return_value = MagicMock()
        mock_email_service.send_verification_email.return_value = None

        input_data = SendVerificationEmailInput(
            user_id="user-123", email="user@example.com"
        )
        use_case = self._make_use_case(
            mock_verification_repository, mock_email_service
        )

        # Act
        with patch(
            "app.use_cases.email_verification.send_verification_email.OAuth2Service"
        ) as MockOAuth:
            MockOAuth.return_value.create_verification_token.return_value = "jwt-token"
            result = await use_case.execute(input_data)

        # Assert
        assert result == "jwt-token"
        mock_verification_repository.invalidate_all_by_user_id.assert_called_once_with(
            "user-123"
        )
        mock_verification_repository.create.assert_called_once()
        mock_email_service.send_verification_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_success_with_previous_token(
        self,
        mock_verification_repository,
        mock_email_service,
        sample_verification_token_entity,
    ):
        # Arrange — previous token exists with resend_count = 1 (below limit)
        sample_verification_token_entity.resend_count = 1
        mock_verification_repository.get_latest_by_user_id.return_value = (
            sample_verification_token_entity
        )
        mock_verification_repository.invalidate_all_by_user_id.return_value = None
        mock_verification_repository.create.return_value = MagicMock()
        mock_email_service.send_verification_email.return_value = None

        input_data = SendVerificationEmailInput(
            user_id="user-123", email="user@example.com"
        )
        use_case = self._make_use_case(
            mock_verification_repository, mock_email_service
        )

        # Act
        with patch(
            "app.use_cases.email_verification.send_verification_email.OAuth2Service"
        ) as MockOAuth:
            MockOAuth.return_value.create_verification_token.return_value = "jwt-token"
            result = await use_case.execute(input_data)

        # Assert
        assert result == "jwt-token"
        mock_verification_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_code_is_hashed_before_storing(
        self,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange
        stored_entity = None

        async def capture_create(entity):
            nonlocal stored_entity
            stored_entity = entity
            return entity

        mock_verification_repository.get_latest_by_user_id.return_value = None
        mock_verification_repository.invalidate_all_by_user_id.return_value = None
        mock_verification_repository.create.side_effect = capture_create
        mock_email_service.send_verification_email.return_value = None

        input_data = SendVerificationEmailInput(
            user_id="user-123", email="user@example.com"
        )
        use_case = self._make_use_case(
            mock_verification_repository, mock_email_service
        )

        # Act
        with patch(
            "app.use_cases.email_verification.send_verification_email.OAuth2Service"
        ) as MockOAuth:
            MockOAuth.return_value.create_verification_token.return_value = "jwt-token"
            with patch(
                "app.use_cases.email_verification.send_verification_email.secrets.randbelow",
                return_value=282910,  # 282910 + 100000 = 382910
            ):
                await use_case.execute(input_data)

        # Assert — code stored as hash, not plain text
        assert stored_entity is not None
        expected_hash = hashlib.sha256("382910".encode()).hexdigest()
        assert stored_entity.code_hash == expected_hash

    # ------------------------------------------------------------------
    # Failure cases
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_raises_value_error_when_resend_limit_reached(
        self,
        mock_verification_repository,
        mock_email_service,
        sample_verification_token_entity,
    ):
        # Arrange — resend_count at limit (3)
        sample_verification_token_entity.resend_count = 3
        mock_verification_repository.get_latest_by_user_id.return_value = (
            sample_verification_token_entity
        )
        input_data = SendVerificationEmailInput(
            user_id="user-123", email="user@example.com"
        )
        use_case = self._make_use_case(
            mock_verification_repository, mock_email_service
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum number"):
            await use_case.execute(input_data)

        mock_verification_repository.create.assert_not_called()
        mock_email_service.send_verification_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_propagates_email_service_exception(
        self,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange
        mock_verification_repository.get_latest_by_user_id.return_value = None
        mock_verification_repository.invalidate_all_by_user_id.return_value = None
        mock_verification_repository.create.return_value = MagicMock()
        mock_email_service.send_verification_email.side_effect = Exception(
            "SMTP error"
        )
        input_data = SendVerificationEmailInput(
            user_id="user-123", email="user@example.com"
        )
        use_case = self._make_use_case(
            mock_verification_repository, mock_email_service
        )

        # Act & Assert
        with pytest.raises(Exception, match="SMTP error"):
            with patch(
                "app.use_cases.email_verification.send_verification_email.OAuth2Service"
            ):
                await use_case.execute(input_data)
