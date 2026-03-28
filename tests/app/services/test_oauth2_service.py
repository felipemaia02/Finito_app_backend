"""Tests for OAuth2 service."""

import pytest
from datetime import datetime, timedelta
from app.services.oauth2_service import OAuth2Service
from app.models.auth_schema import TokenData


@pytest.fixture
def oauth2_service():
    """Provide OAuth2 service instance."""
    return OAuth2Service()


class TestOAuth2ServicePasswordHashing:
    """Test password hashing functionality."""

    def test_hash_password_creates_hash(self, oauth2_service):
        """Test that hash_password creates a valid hash."""
        # Arrange
        password = "test_password_123"

        # Act
        hashed = oauth2_service.hash_password(password)

        # Assert
        assert hashed != password
        assert len(hashed) > 0
        assert "$2b$" in hashed  # bcrypt prefix

    def test_hash_password_different_results(self, oauth2_service):
        """Test that same password produces different hashes"""
        # Arrange
        password = "test123"

        # Act
        hash1 = oauth2_service.hash_password(password)
        hash2 = oauth2_service.hash_password(password)

        # Assert
        assert hash1 != hash2  # bcrypt uses salt, hashes differ

    def test_verify_password_success(self, oauth2_service):
        """Test password verification with correct password."""
        # Arrange
        password = "test_password_123"
        hashed = oauth2_service.hash_password(password)

        # Act
        is_valid = oauth2_service.verify_password(password, hashed)

        # Assert
        assert is_valid is True

    def test_verify_password_wrong_password(self, oauth2_service):
        """Test password verification with wrong password."""
        # Arrange
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = oauth2_service.hash_password(password)

        # Act
        is_valid = oauth2_service.verify_password(wrong_password, hashed)

        # Assert
        assert is_valid is False

    def test_verify_password_empty_password(self, oauth2_service):
        """Test password verification with empty password."""
        # Arrange
        password = "test_password_123"
        hashed = oauth2_service.hash_password(password)

        # Act
        is_valid = oauth2_service.verify_password("", hashed)

        # Assert
        assert is_valid is False


class TestOAuth2ServiceTokenGeneration:
    """Test token generation functionality."""

    def test_create_access_token(self, oauth2_service):
        """Test access token creation."""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        token = oauth2_service.create_access_token(data)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT format: header.payload.signature
        assert token.count(".") == 2

    def test_create_access_token_with_custom_expiration(self, oauth2_service):
        """Test access token with custom expiration."""
        # Arrange
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(hours=2)

        # Act
        token = oauth2_service.create_access_token(data, expires_delta)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, oauth2_service):
        """Test refresh token creation."""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        token = oauth2_service.create_refresh_token(data)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count(".") == 2

    def test_create_refresh_token_with_custom_expiration(self, oauth2_service):
        """Test refresh token with custom expiration."""
        # Arrange
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(days=30)

        # Act
        token = oauth2_service.create_refresh_token(data, expires_delta)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_pair(self, oauth2_service):
        """Test creating both access and refresh tokens."""
        # Arrange
        email = "test@example.com"

        # Act
        access_token, refresh_token, expires_at = oauth2_service.create_token_pair(
            email
        )

        # Assert
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert isinstance(expires_at, datetime)
        assert access_token != refresh_token


class TestOAuth2ServiceTokenVerification:
    """Test token verification functionality."""

    def test_verify_access_token_valid(self, oauth2_service):
        """Test verification of valid access token."""
        # Arrange
        email = "test@example.com"
        access_token, _, _ = oauth2_service.create_token_pair(email)

        # Act
        token_data = oauth2_service.verify_token(access_token, token_type="access")

        # Assert
        assert token_data is not None
        assert isinstance(token_data, TokenData)
        assert token_data.sub == email
        assert token_data.type == "access"

    def test_verify_refresh_token_valid(self, oauth2_service):
        """Test verification of valid refresh token."""
        # Arrange
        email = "test@example.com"
        _, refresh_token, _ = oauth2_service.create_token_pair(email)

        # Act
        token_data = oauth2_service.verify_token(refresh_token, token_type="refresh")

        # Assert
        assert token_data is not None
        assert isinstance(token_data, TokenData)
        assert token_data.sub == email
        assert token_data.type == "refresh"

    def test_verify_access_token_with_wrong_type(self, oauth2_service):
        """Test that access token fails when expecting refresh type."""
        # Arrange
        email = "test@example.com"
        access_token, _, _ = oauth2_service.create_token_pair(email)

        # Act
        token_data = oauth2_service.verify_token(access_token, token_type="refresh")

        # Assert
        assert token_data is None  # Token type mismatch

    def test_verify_refresh_token_with_wrong_type(self, oauth2_service):
        """Test that refresh token fails when expecting access type."""
        # Arrange
        email = "test@example.com"
        _, refresh_token, _ = oauth2_service.create_token_pair(email)

        # Act
        token_data = oauth2_service.verify_token(refresh_token, token_type="access")

        # Assert
        assert token_data is None  # Token type mismatch

    def test_verify_token_missing_exp_claim(self, oauth2_service):
        """Test verification of token with 'sub' but missing 'exp' returns None."""
        # Arrange
        import jwt

        payload = {"sub": "test@example.com", "type": "access"}  # Missing 'exp'
        token = jwt.encode(
            payload,
            oauth2_service.settings.secret_key,
            algorithm=oauth2_service.algorithm,
        )

        # Act
        token_data = oauth2_service.verify_token(token, token_type="access")

        # Assert
        assert token_data is None

    def test_verify_invalid_token(self, oauth2_service):
        """Test verification of invalid token."""
        # Arrange
        invalid_token = "invalid.token.here"

        # Act
        token_data = oauth2_service.verify_token(invalid_token)

        # Assert
        assert token_data is None

    def test_verify_expired_token(self, oauth2_service):
        """Test verification of expired token."""
        # Arrange
        email = "test@example.com"
        # Create token with very short expiration
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = oauth2_service.create_access_token(
            data={"sub": email}, expires_delta=expires_delta
        )

        # Act
        token_data = oauth2_service.verify_token(token, token_type="access")

        # Assert
        assert token_data is None  # Token is expired

    def test_verify_token_missing_sub_claim(self, oauth2_service):
        """Test verification of token missing 'sub' claim."""
        # Arrange
        import jwt

        payload = {"type": "access"}  # Missing 'sub'
        token = jwt.encode(
            payload,
            oauth2_service.settings.secret_key,
            algorithm=oauth2_service.algorithm,
        )

        # Act
        token_data = oauth2_service.verify_token(token, token_type="access")

        # Assert
        assert token_data is None

    def test_verify_token_returns_token_data(self, oauth2_service):
        """Test that token_data contains correct information."""
        # Arrange
        email = "john@example.com"
        token, _, _ = oauth2_service.create_token_pair(email)

        # Act
        token_data = oauth2_service.verify_token(token, token_type="access")

        # Assert
        assert token_data is not None
        assert token_data.sub == email
        assert token_data.type == "access"
        assert token_data.exp is not None
        assert isinstance(token_data.exp, int)


class TestOAuth2ServiceIntegration:
    """Integration tests for OAuth2 service."""

    def test_full_auth_flow(self, oauth2_service):
        """Test complete authentication flow."""
        # Arrange
        email = "user@example.com"

        # Act
        # 1. Create tokens
        access_token, refresh_token, expires_at = oauth2_service.create_token_pair(
            email
        )

        # 2. Verify access token
        access_token_data = oauth2_service.verify_token(
            access_token, token_type="access"
        )

        # 3. Verify refresh token
        refresh_token_data = oauth2_service.verify_token(
            refresh_token, token_type="refresh"
        )

        # Assert
        assert access_token_data is not None
        assert access_token_data.sub == email
        assert refresh_token_data is not None
        assert refresh_token_data.sub == email
        assert isinstance(expires_at, datetime)

    def test_verify_password_returns_false_on_bcrypt_exception(self, oauth2_service, mocker):
        """Test verify_password returns False when bcrypt raises an exception."""
        # Arrange
        mocker.patch("bcrypt.checkpw", side_effect=ValueError("bad hash"))

        # Act
        result = oauth2_service.verify_password("password", "invalid_hash")

        # Assert
        assert result is False
