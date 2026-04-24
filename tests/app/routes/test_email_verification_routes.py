"""Tests for routes/email_verification_routes.py"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.api import app
from app.infrastructure.settings import get_settings
from app.infrastructure.dependencies.email_verification_dependencies import (
    EmailVerificationDependencies,
)


def make_token_response():
    from app.models.auth_schema import TokenResponse

    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    return TokenResponse(
        access_token="access-token",
        refresh_token="refresh-token",
        token_type="bearer",
        expires_in=3600,
        expires_at=expires_at,
    )


def make_standard_response(message: str = "OK"):
    from app.models.response_schema import StandardResponse

    return StandardResponse(message=message)


def make_register_response(token: str = "jwt-token"):
    from app.models.email_verification_schema import UserRegisterResponse

    return UserRegisterResponse(
        message="If this email is registered and unverified, a code has been sent.",
        verification_token=token,
    )


@pytest.fixture
def api_key():
    return get_settings().api_key


@pytest.fixture
def ev_client(api_key, valid_verification_token):
    """
    Test client with:
    - API key header
    - verification JWT in Authorization header
    - EmailVerificationController mocked
    """
    mock_controller = AsyncMock()
    app.dependency_overrides[EmailVerificationDependencies.get_controller] = (
        lambda: mock_controller
    )
    client = TestClient(app, raise_server_exceptions=False)
    client.headers.update(
        {
            "X-API-Key": api_key,
            "Authorization": f"Bearer {valid_verification_token}",
        }
    )
    yield client, mock_controller
    app.dependency_overrides.pop(EmailVerificationDependencies.get_controller, None)


@pytest.fixture
def public_ev_client(api_key):
    """Test client with only API key (for /request-verification)."""
    mock_controller = AsyncMock()
    app.dependency_overrides[EmailVerificationDependencies.get_controller] = (
        lambda: mock_controller
    )
    client = TestClient(app, raise_server_exceptions=False)
    client.headers.update({"X-API-Key": api_key})
    yield client, mock_controller
    app.dependency_overrides.pop(EmailVerificationDependencies.get_controller, None)


class TestVerifyEmailRoute:
    """Tests for POST /api/v1/auth/verify-email"""

    def test_verify_email_success(self, ev_client):
        # Arrange
        client, mock_controller = ev_client
        mock_controller.verify_email = AsyncMock(return_value=make_token_response())

        # Act
        response = client.post("/api/v1/auth/verify-email", json={"code": "382910"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "access-token"
        assert data["token_type"] == "bearer"
        mock_controller.verify_email.assert_called_once()

    def test_verify_email_invalid_code_returns_422(self, ev_client):
        # Arrange
        client, mock_controller = ev_client
        mock_controller.verify_email = AsyncMock(
            side_effect=ValueError("Invalid verification code. 2 attempts remaining.")
        )

        # Act
        response = client.post("/api/v1/auth/verify-email", json={"code": "000000"})

        # Assert
        assert response.status_code == 422
        assert "Invalid verification code" in response.json()["detail"]

    def test_verify_email_expired_code_returns_422(self, ev_client):
        # Arrange
        client, mock_controller = ev_client
        mock_controller.verify_email = AsyncMock(
            side_effect=ValueError("Verification code has expired.")
        )

        # Act
        response = client.post("/api/v1/auth/verify-email", json={"code": "123456"})

        # Assert
        assert response.status_code == 422
        assert "expired" in response.json()["detail"].lower()

    def test_verify_email_infrastructure_error_returns_400(self, ev_client):
        # Arrange
        client, mock_controller = ev_client
        mock_controller.verify_email = AsyncMock(
            side_effect=Exception("DB connection lost")
        )

        # Act
        response = client.post("/api/v1/auth/verify-email", json={"code": "382910"})

        # Assert
        assert response.status_code == 400

    def test_verify_email_missing_code_returns_422(self, ev_client):
        # Arrange
        client, _ = ev_client

        # Act
        response = client.post("/api/v1/auth/verify-email", json={})

        # Assert
        assert response.status_code == 422

    def test_verify_email_code_too_short_returns_422(self, ev_client):
        # Arrange
        client, _ = ev_client

        # Act
        response = client.post("/api/v1/auth/verify-email", json={"code": "123"})

        # Assert
        assert response.status_code == 422

    def test_verify_email_without_bearer_token_returns_403_or_401(self, api_key):
        # Arrange — no Authorization header
        mock_controller = AsyncMock()
        app.dependency_overrides[EmailVerificationDependencies.get_controller] = (
            lambda: mock_controller
        )
        client = TestClient(app, raise_server_exceptions=False)
        client.headers.update({"X-API-Key": api_key})

        try:
            # Act
            response = client.post(
                "/api/v1/auth/verify-email", json={"code": "382910"}
            )

            # Assert
            assert response.status_code in [401, 403, 422]
        finally:
            app.dependency_overrides.pop(
                EmailVerificationDependencies.get_controller, None
            )

    def test_verify_email_without_api_key_returns_403(self, valid_verification_token):
        # Arrange
        mock_controller = AsyncMock()
        app.dependency_overrides[EmailVerificationDependencies.get_controller] = (
            lambda: mock_controller
        )
        client = TestClient(app, raise_server_exceptions=False)
        client.headers.update(
            {"Authorization": f"Bearer {valid_verification_token}"}
        )

        try:
            # Act
            response = client.post(
                "/api/v1/auth/verify-email", json={"code": "382910"}
            )

            # Assert
            assert response.status_code in [401, 403, 422]
        finally:
            app.dependency_overrides.pop(
                EmailVerificationDependencies.get_controller, None
            )


class TestResendVerificationRoute:
    """Tests for POST /api/v1/auth/resend-verification"""

    def test_resend_success(self, ev_client):
        # Arrange
        client, mock_controller = ev_client
        mock_controller.resend_verification = AsyncMock(
            return_value=make_standard_response(
                "Verification email sent. Please check your inbox."
            )
        )

        # Act
        response = client.post("/api/v1/auth/resend-verification")

        # Assert
        assert response.status_code == 200
        assert "inbox" in response.json()["message"].lower()
        mock_controller.resend_verification.assert_called_once()

    def test_resend_already_verified_returns_422(self, ev_client):
        # Arrange
        client, mock_controller = ev_client
        mock_controller.resend_verification = AsyncMock(
            side_effect=ValueError("Email is already verified.")
        )

        # Act
        response = client.post("/api/v1/auth/resend-verification")

        # Assert
        assert response.status_code == 422
        assert "verified" in response.json()["detail"].lower()

    def test_resend_limit_reached_returns_422(self, ev_client):
        # Arrange
        client, mock_controller = ev_client
        mock_controller.resend_verification = AsyncMock(
            side_effect=ValueError("Maximum number of verification email resends reached.")
        )

        # Act
        response = client.post("/api/v1/auth/resend-verification")

        # Assert
        assert response.status_code == 422
        assert "maximum" in response.json()["detail"].lower()

    def test_resend_infrastructure_error_returns_400(self, ev_client):
        # Arrange
        client, mock_controller = ev_client
        mock_controller.resend_verification = AsyncMock(
            side_effect=Exception("Unexpected error")
        )

        # Act
        response = client.post("/api/v1/auth/resend-verification")

        # Assert
        assert response.status_code == 400

    def test_resend_without_bearer_returns_401_or_403(self, api_key):
        # Arrange — no Authorization header
        mock_controller = AsyncMock()
        app.dependency_overrides[EmailVerificationDependencies.get_controller] = (
            lambda: mock_controller
        )
        client = TestClient(app, raise_server_exceptions=False)
        client.headers.update({"X-API-Key": api_key})

        try:
            # Act
            response = client.post("/api/v1/auth/resend-verification")

            # Assert
            assert response.status_code in [401, 403, 422]
        finally:
            app.dependency_overrides.pop(
                EmailVerificationDependencies.get_controller, None
            )


class TestRequestVerificationRoute:
    """Tests for POST /api/v1/auth/request-verification"""

    def test_request_verification_success_with_token(self, public_ev_client):
        # Arrange
        client, mock_controller = public_ev_client
        mock_controller.request_verification = AsyncMock(
            return_value=make_register_response("jwt-token")
        )

        # Act
        response = client.post(
            "/api/v1/auth/request-verification",
            json={"email": "maria@example.com"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["verification_token"] == "jwt-token"
        mock_controller.request_verification.assert_called_once_with(
            email="maria@example.com"
        )

    def test_request_verification_generic_response_no_token(self, public_ev_client):
        # Arrange — user not found → empty token (opaque response)
        client, mock_controller = public_ev_client
        mock_controller.request_verification = AsyncMock(
            return_value=make_register_response("")
        )

        # Act
        response = client.post(
            "/api/v1/auth/request-verification",
            json={"email": "ghost@example.com"},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["verification_token"] == ""

    def test_request_verification_invalid_email_returns_422(self, public_ev_client):
        # Arrange
        client, _ = public_ev_client

        # Act
        response = client.post(
            "/api/v1/auth/request-verification",
            json={"email": "not-an-email"},
        )

        # Assert
        assert response.status_code == 422

    def test_request_verification_missing_body_returns_422(self, public_ev_client):
        # Arrange
        client, _ = public_ev_client

        # Act
        response = client.post("/api/v1/auth/request-verification", json={})

        # Assert
        assert response.status_code == 422

    def test_request_verification_infrastructure_error_returns_400(
        self, public_ev_client
    ):
        # Arrange
        client, mock_controller = public_ev_client
        mock_controller.request_verification = AsyncMock(
            side_effect=Exception("DB error")
        )

        # Act
        response = client.post(
            "/api/v1/auth/request-verification",
            json={"email": "maria@example.com"},
        )

        # Assert
        assert response.status_code == 400

    def test_request_verification_without_api_key_returns_403(self):
        # Arrange
        mock_controller = AsyncMock()
        app.dependency_overrides[EmailVerificationDependencies.get_controller] = (
            lambda: mock_controller
        )
        client = TestClient(app, raise_server_exceptions=False)

        try:
            # Act
            response = client.post(
                "/api/v1/auth/request-verification",
                json={"email": "maria@example.com"},
            )

            # Assert
            assert response.status_code in [401, 403, 422]
        finally:
            app.dependency_overrides.pop(
                EmailVerificationDependencies.get_controller, None
            )
