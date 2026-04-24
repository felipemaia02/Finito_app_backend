"""Tests for domain/entities/email_verification_token_entity.py"""

import pytest
import time
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError

from app.domain.entities.email_verification_token_entity import EmailVerificationToken


class TestEmailVerificationTokenCreation:
    def test_create_with_required_fields(self):
        # Arrange / Act
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = EmailVerificationToken(
            user_id="user-123",
            code_hash="abc123hash",
            expires_at=expires_at,
        )

        # Assert
        assert token.user_id == "user-123"
        assert token.code_hash == "abc123hash"
        assert token.expires_at == expires_at
        assert token.is_used is False
        assert token.attempts == 0
        assert token.resend_count == 0
        assert token.id is None
        assert token.created_at is not None
        assert token.updated_at is not None

    def test_create_with_all_fields(self, sample_verification_token_data):
        # Arrange / Act
        token = EmailVerificationToken(**sample_verification_token_data)

        # Assert
        assert token.user_id == sample_verification_token_data["user_id"]
        assert token.code_hash == sample_verification_token_data["code_hash"]
        assert token.is_used == sample_verification_token_data["is_used"]
        assert token.attempts == sample_verification_token_data["attempts"]
        assert token.resend_count == sample_verification_token_data["resend_count"]

    def test_create_with_custom_defaults(self):
        # Arrange / Act
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = EmailVerificationToken(
            user_id="user-456",
            code_hash="hashvalue",
            expires_at=expires_at,
            is_used=True,
            attempts=3,
            resend_count=2,
        )

        # Assert
        assert token.is_used is True
        assert token.attempts == 3
        assert token.resend_count == 2


class TestEmailVerificationTokenDefaults:
    def test_is_used_defaults_to_false(self):
        # Arrange / Act
        token = EmailVerificationToken(
            user_id="u",
            code_hash="h",
            expires_at=datetime.now(timezone.utc),
        )

        # Assert
        assert token.is_used is False

    def test_attempts_defaults_to_zero(self):
        # Arrange / Act
        token = EmailVerificationToken(
            user_id="u",
            code_hash="h",
            expires_at=datetime.now(timezone.utc),
        )

        # Assert
        assert token.attempts == 0

    def test_resend_count_defaults_to_zero(self):
        # Arrange / Act
        token = EmailVerificationToken(
            user_id="u",
            code_hash="h",
            expires_at=datetime.now(timezone.utc),
        )

        # Assert
        assert token.resend_count == 0

    def test_id_defaults_to_none(self):
        # Arrange / Act
        token = EmailVerificationToken(
            user_id="u",
            code_hash="h",
            expires_at=datetime.now(timezone.utc),
        )

        # Assert
        assert token.id is None


class TestEmailVerificationTokenValidation:
    def test_user_id_required(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            EmailVerificationToken(
                code_hash="hash",
                expires_at=datetime.now(timezone.utc),
            )

    def test_code_hash_required(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            EmailVerificationToken(
                user_id="user-123",
                expires_at=datetime.now(timezone.utc),
            )

    def test_expires_at_required(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            EmailVerificationToken(
                user_id="user-123",
                code_hash="hash",
            )

    def test_missing_all_required_fields(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            EmailVerificationToken()


class TestEmailVerificationTokenUpdateTimestamp:
    def test_update_timestamp_changes_updated_at(
        self, sample_verification_token_entity
    ):
        # Arrange
        original_updated_at = sample_verification_token_entity.updated_at

        # Act
        time.sleep(0.001)
        sample_verification_token_entity.update_timestamp()

        # Assert
        assert sample_verification_token_entity.updated_at > original_updated_at

    def test_update_timestamp_keeps_created_at_unchanged(
        self, sample_verification_token_entity
    ):
        # Arrange
        original_created_at = sample_verification_token_entity.created_at

        # Act
        sample_verification_token_entity.update_timestamp()

        # Assert
        assert sample_verification_token_entity.created_at == original_created_at


class TestEmailVerificationTokenMutability:
    def test_is_used_can_be_set(self, sample_verification_token_entity):
        # Arrange
        assert sample_verification_token_entity.is_used is False

        # Act
        sample_verification_token_entity.is_used = True

        # Assert
        assert sample_verification_token_entity.is_used is True

    def test_attempts_can_be_incremented(self, sample_verification_token_entity):
        # Arrange
        initial_attempts = sample_verification_token_entity.attempts

        # Act
        sample_verification_token_entity.attempts += 1

        # Assert
        assert sample_verification_token_entity.attempts == initial_attempts + 1

    def test_resend_count_can_be_incremented(self, sample_verification_token_entity):
        # Arrange
        initial_resend_count = sample_verification_token_entity.resend_count

        # Act
        sample_verification_token_entity.resend_count += 1

        # Assert
        assert sample_verification_token_entity.resend_count == initial_resend_count + 1
