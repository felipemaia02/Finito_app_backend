"""Tests for use_cases/email_verification/verify_email_code.py"""

import hashlib
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta

from app.use_cases.email_verification.verify_email_code import VerifyEmailCodeUseCase
from app.domain.dtos.email_verification_dtos import VerifyEmailCodeInput


VALID_CODE = "382910"
VALID_HASH = hashlib.sha256(VALID_CODE.encode()).hexdigest()
WRONG_CODE = "000000"


class TestVerifyEmailCodeUseCase:
    """Tests for VerifyEmailCodeUseCase."""

    def _make_use_case(self, mock_user_repository, mock_verification_repository):
        return VerifyEmailCodeUseCase(
            user_repository=mock_user_repository,
            verification_repository=mock_verification_repository,
        )

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_verify_success_activates_user_and_returns_tokens(
        self,
        mock_user_repository,
        mock_verification_repository,
        sample_verification_token_entity,
        sample_unverified_user_entity,
    ):
        # Arrange
        sample_verification_token_entity.code_hash = VALID_HASH
        sample_verification_token_entity.attempts = 0
        mock_verification_repository.get_valid_token_by_user_id.return_value = (
            sample_verification_token_entity
        )
        mock_verification_repository.mark_as_used.return_value = None
        mock_user_repository.get_by_id_unverified.return_value = (
            sample_unverified_user_entity
        )
        mock_user_repository.update.return_value = sample_unverified_user_entity

        input_data = VerifyEmailCodeInput(
            user_id=sample_unverified_user_entity.id, code=VALID_CODE
        )
        use_case = self._make_use_case(mock_user_repository, mock_verification_repository)

        # Act
        with patch(
            "app.use_cases.email_verification.verify_email_code.OAuth2Service"
        ) as MockOAuth:
            mock_oauth = MockOAuth.return_value
            future_dt = datetime.now(timezone.utc) + timedelta(hours=1)
            mock_oauth.create_token_pair.return_value = (
                "access-token",
                "refresh-token",
                future_dt,
            )
            result = await use_case.execute(input_data)

        # Assert
        assert result.access_token == "access-token"
        assert result.refresh_token == "refresh-token"
        assert result.token_type == "bearer"
        mock_verification_repository.mark_as_used.assert_called_once_with(
            sample_verification_token_entity.id
        )
        mock_user_repository.update.assert_called_once()
        # User must be activated
        assert sample_unverified_user_entity.is_active is True
        assert sample_unverified_user_entity.is_email_verified is True

    # ------------------------------------------------------------------
    # Failure cases
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_raises_when_no_active_token_found(
        self, mock_user_repository, mock_verification_repository
    ):
        # Arrange
        mock_verification_repository.get_valid_token_by_user_id.return_value = None
        use_case = self._make_use_case(mock_user_repository, mock_verification_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="No active verification token"):
            await use_case.execute(
                VerifyEmailCodeInput(user_id="user-123", code=VALID_CODE)
            )
        mock_user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_when_token_expired(
        self,
        mock_user_repository,
        mock_verification_repository,
        sample_verification_token_entity,
    ):
        # Arrange — token expired 1 minute ago
        sample_verification_token_entity.expires_at = datetime.now(
            timezone.utc
        ) - timedelta(minutes=1)
        mock_verification_repository.get_valid_token_by_user_id.return_value = (
            sample_verification_token_entity
        )
        use_case = self._make_use_case(mock_user_repository, mock_verification_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="expired"):
            await use_case.execute(
                VerifyEmailCodeInput(
                    user_id=sample_verification_token_entity.user_id, code=VALID_CODE
                )
            )
        mock_user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_when_max_attempts_exceeded(
        self,
        mock_user_repository,
        mock_verification_repository,
        sample_verification_token_entity,
    ):
        # Arrange — already at 5 attempts
        sample_verification_token_entity.attempts = 5
        mock_verification_repository.get_valid_token_by_user_id.return_value = (
            sample_verification_token_entity
        )
        use_case = self._make_use_case(mock_user_repository, mock_verification_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Too many failed attempts"):
            await use_case.execute(
                VerifyEmailCodeInput(
                    user_id=sample_verification_token_entity.user_id, code=VALID_CODE
                )
            )
        mock_user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_and_increments_attempts_on_wrong_code(
        self,
        mock_user_repository,
        mock_verification_repository,
        sample_verification_token_entity,
    ):
        # Arrange
        sample_verification_token_entity.code_hash = VALID_HASH
        sample_verification_token_entity.attempts = 2
        mock_verification_repository.get_valid_token_by_user_id.return_value = (
            sample_verification_token_entity
        )
        mock_verification_repository.increment_attempts.return_value = None
        use_case = self._make_use_case(mock_user_repository, mock_verification_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid verification code"):
            await use_case.execute(
                VerifyEmailCodeInput(
                    user_id=sample_verification_token_entity.user_id, code=WRONG_CODE
                )
            )

        mock_verification_repository.increment_attempts.assert_called_once_with(
            sample_verification_token_entity.id
        )
        mock_user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_remaining_attempts_reported_correctly(
        self,
        mock_user_repository,
        mock_verification_repository,
        sample_verification_token_entity,
    ):
        # Arrange — 1 attempt already done, submit wrong code → 3 remaining
        sample_verification_token_entity.code_hash = VALID_HASH
        sample_verification_token_entity.attempts = 1
        mock_verification_repository.get_valid_token_by_user_id.return_value = (
            sample_verification_token_entity
        )
        mock_verification_repository.increment_attempts.return_value = None
        use_case = self._make_use_case(mock_user_repository, mock_verification_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="3 attempts remaining"):
            await use_case.execute(
                VerifyEmailCodeInput(
                    user_id=sample_verification_token_entity.user_id, code=WRONG_CODE
                )
            )

    @pytest.mark.asyncio
    async def test_raises_when_user_not_found_after_token_validation(
        self,
        mock_user_repository,
        mock_verification_repository,
        sample_verification_token_entity,
    ):
        # Arrange — token valid but user was deleted between steps
        sample_verification_token_entity.code_hash = VALID_HASH
        sample_verification_token_entity.attempts = 0
        mock_verification_repository.get_valid_token_by_user_id.return_value = (
            sample_verification_token_entity
        )
        mock_verification_repository.mark_as_used.return_value = None
        mock_user_repository.get_by_id_unverified.return_value = None
        use_case = self._make_use_case(mock_user_repository, mock_verification_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            await use_case.execute(
                VerifyEmailCodeInput(
                    user_id=sample_verification_token_entity.user_id, code=VALID_CODE
                )
            )
        mock_user_repository.update.assert_not_called()
