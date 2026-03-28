"""Tests for use_cases/user/password_utils.py"""

import pytest
from app.use_cases.user.password_utils import hash_password, verify_password


class TestPasswordUtils:
    """Test cases for password hashing and verification utilities."""

    def test_hash_password_creates_bcrypt_hash(self):
        """Test that hash_password creates a valid bcrypt hash."""
        # Arrange
        password = "my_secure_password"

        # Act
        hashed = hash_password(password)

        # Assert
        assert hashed is not None
        assert hashed.startswith("$2b$")  # bcrypt format
        assert hashed != password  # Should not be plaintext

    def test_hash_password_different_results(self):
        """Test that same password produces different hashes (due to salt)."""
        # Arrange
        password = "my_secure_password"

        # Act
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Assert
        assert hash1 != hash2  # Different salts produce different hashes

    def test_verify_password_success(self):
        """Test successful password verification."""
        # Arrange
        password = "my_secure_password"
        hashed = hash_password(password)

        # Act
        result = verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_wrong_password(self):
        """Test verification fails with wrong password."""
        # Arrange
        password = "my_secure_password"
        hashed = hash_password(password)
        wrong_password = "wrong_password"

        # Act
        result = verify_password(wrong_password, hashed)

        # Assert
        assert result is False

    def test_verify_password_empty_password(self):
        """Test verification with empty password."""
        # Arrange
        password = "my_secure_password"
        hashed = hash_password(password)

        # Act
        result = verify_password("", hashed)

        # Assert
        assert result is False

    def test_hash_and_verify_roundtrip(self):
        """Test complete hash and verify roundtrip."""
        # Arrange
        passwords = [
            "simple_password",
            "complex_p@ssw0rd!#$%",
            "password_with_unicode_çãõ",
            "very_long_password_with_special_chars_123!@#",
        ]

        # Act & Assert
        for password in passwords:
            hashed = hash_password(password)
            assert verify_password(password, hashed) is True
            assert verify_password("wrong", hashed) is False
