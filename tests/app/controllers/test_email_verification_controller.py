"""Tests for controllers/email_verification_controller.py"""

import pytest
from unittest.mock import AsyncMock, patch

from app.controllers.email_verification_controller import EmailVerificationController
from app.domain.dtos.email_verification_dtos import (
    VerifyEmailCodeInput,
    ResendVerificationEmailInput,
    RequestVerificationInput,
)


class TestEmailVerificationController:
    """Tests for EmailVerificationController — verifies delegation to use cases."""

    def _make_controller(
        self, mock_user_repository, mock_verification_repository, mock_email_service
    ):
        return EmailVerificationController(
            user_repository=mock_user_repository,
            verification_repository=mock_verification_repository,
            email_service=mock_email_service,
        )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def test_controller_initializes_all_use_cases(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange & Act
        controller = self._make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )

        # Assert
        assert controller.verify_use_case is not None
        assert controller.resend_use_case is not None
        assert controller.request_use_case is not None

    # ------------------------------------------------------------------
    # verify_email
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_verify_email_delegates_to_use_case(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange
        controller = self._make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )
        mock_result = AsyncMock()
        controller.verify_use_case.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await controller.verify_email(user_id="user-123", code="382910")

        # Assert
        controller.verify_use_case.execute.assert_called_once_with(
            VerifyEmailCodeInput(user_id="user-123", code="382910")
        )
        assert result is mock_result

    # ------------------------------------------------------------------
    # resend_verification
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_resend_verification_delegates_to_use_case(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange
        controller = self._make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )
        mock_result = AsyncMock()
        controller.resend_use_case.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await controller.resend_verification(user_id="user-123")

        # Assert
        controller.resend_use_case.execute.assert_called_once_with(
            ResendVerificationEmailInput(user_id="user-123")
        )
        assert result is mock_result

    # ------------------------------------------------------------------
    # request_verification
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_request_verification_delegates_to_use_case(
        self,
        mock_user_repository,
        mock_verification_repository,
        mock_email_service,
    ):
        # Arrange
        controller = self._make_controller(
            mock_user_repository, mock_verification_repository, mock_email_service
        )
        mock_result = AsyncMock()
        controller.request_use_case.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await controller.request_verification(email="user@example.com")

        # Assert
        controller.request_use_case.execute.assert_called_once_with(
            RequestVerificationInput(email="user@example.com")
        )
        assert result is mock_result
