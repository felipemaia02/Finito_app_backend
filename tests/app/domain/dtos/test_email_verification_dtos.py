"""Tests for domain/dtos/email_verification_dtos.py"""

import pytest

from app.domain.dtos.email_verification_dtos import (
    SendVerificationEmailInput,
    VerifyEmailCodeInput,
    ResendVerificationEmailInput,
    RequestVerificationInput,
)


class TestSendVerificationEmailInput:
    def test_create_with_valid_fields(self):
        # Arrange / Act
        dto = SendVerificationEmailInput(user_id="user-123", email="user@example.com")

        # Assert
        assert dto.user_id == "user-123"
        assert dto.email == "user@example.com"

    def test_is_named_tuple(self):
        # Arrange
        dto = SendVerificationEmailInput(user_id="u", email="e@e.com")

        # Act / Assert — NamedTuples are immutable
        with pytest.raises(AttributeError):
            dto.user_id = "other"

    def test_supports_positional_unpacking(self):
        # Arrange
        dto = SendVerificationEmailInput(user_id="uid", email="mail@mail.com")

        # Act
        user_id, email = dto

        # Assert
        assert user_id == "uid"
        assert email == "mail@mail.com"

    def test_equality_by_value(self):
        # Arrange / Act
        dto1 = SendVerificationEmailInput(user_id="u", email="e@e.com")
        dto2 = SendVerificationEmailInput(user_id="u", email="e@e.com")

        # Assert
        assert dto1 == dto2

    def test_inequality_different_values(self):
        # Arrange / Act
        dto1 = SendVerificationEmailInput(user_id="u1", email="e@e.com")
        dto2 = SendVerificationEmailInput(user_id="u2", email="e@e.com")

        # Assert
        assert dto1 != dto2


class TestVerifyEmailCodeInput:
    def test_create_with_valid_fields(self):
        # Arrange / Act
        dto = VerifyEmailCodeInput(user_id="user-123", code="382910")

        # Assert
        assert dto.user_id == "user-123"
        assert dto.code == "382910"

    def test_is_named_tuple(self):
        # Arrange
        dto = VerifyEmailCodeInput(user_id="u", code="000000")

        # Act / Assert
        with pytest.raises(AttributeError):
            dto.code = "111111"

    def test_supports_positional_unpacking(self):
        # Arrange
        dto = VerifyEmailCodeInput(user_id="uid", code="123456")

        # Act
        user_id, code = dto

        # Assert
        assert user_id == "uid"
        assert code == "123456"

    def test_equality_by_value(self):
        # Arrange / Act
        dto1 = VerifyEmailCodeInput(user_id="u", code="123456")
        dto2 = VerifyEmailCodeInput(user_id="u", code="123456")

        # Assert
        assert dto1 == dto2


class TestResendVerificationEmailInput:
    def test_create_with_user_id(self):
        # Arrange / Act
        dto = ResendVerificationEmailInput(user_id="user-456")

        # Assert
        assert dto.user_id == "user-456"

    def test_is_named_tuple(self):
        # Arrange
        dto = ResendVerificationEmailInput(user_id="u")

        # Act / Assert
        with pytest.raises(AttributeError):
            dto.user_id = "other"

    def test_has_one_field(self):
        # Arrange
        dto = ResendVerificationEmailInput(user_id="uid")

        # Act — unpack to verify structure
        (user_id,) = dto

        # Assert
        assert user_id == "uid"

    def test_equality_by_value(self):
        # Arrange / Act
        dto1 = ResendVerificationEmailInput(user_id="u")
        dto2 = ResendVerificationEmailInput(user_id="u")

        # Assert
        assert dto1 == dto2


class TestRequestVerificationInput:
    def test_create_with_email(self):
        # Arrange / Act
        dto = RequestVerificationInput(email="user@example.com")

        # Assert
        assert dto.email == "user@example.com"

    def test_is_named_tuple(self):
        # Arrange
        dto = RequestVerificationInput(email="e@e.com")

        # Act / Assert
        with pytest.raises(AttributeError):
            dto.email = "other@other.com"

    def test_has_one_field(self):
        # Arrange
        dto = RequestVerificationInput(email="mail@mail.com")

        # Act
        (email,) = dto

        # Assert
        assert email == "mail@mail.com"

    def test_equality_by_value(self):
        # Arrange / Act
        dto1 = RequestVerificationInput(email="a@a.com")
        dto2 = RequestVerificationInput(email="a@a.com")

        # Assert
        assert dto1 == dto2
