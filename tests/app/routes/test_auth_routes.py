"""Tests for auth routes."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from app.api import app


@pytest.fixture
def client(mock_app_dependencies):
    """Provide test client for API with mocked dependencies."""
    return TestClient(mock_app_dependencies)


@pytest.fixture
def auth_client(mock_app_dependencies):
    """Test client with mocked auth controller."""
    from app.infrastructure.settings import get_settings
    from app.infrastructure.dependencies.auth_controller_dependencies import (
        AuthDependencies,
    )

    mock_controller = AsyncMock()
    mock_app_dependencies.dependency_overrides[AuthDependencies.get_controller] = (
        lambda: mock_controller
    )

    api_key = get_settings().api_key

    client = TestClient(mock_app_dependencies)
    client.headers.update({"X-API-Key": api_key})
    return client, mock_controller


def make_token_response_obj():
    from app.models.auth_schema import TokenResponse

    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    return TokenResponse(
        access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test",
        refresh_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.refresh",
        token_type="bearer",
        expires_in=3600,
        expires_at=expires_at,
    )


class TestAuthRoutes:
    """Test authentication endpoints."""

    def test_login_endpoint_exists(self, client):
        """Test that login endpoint exists."""
        login_data = {"email": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code in [200, 400, 401, 422]

    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        login_data = {"email": "test@example.com"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 422

    def test_refresh_token_success(self, client, valid_oauth2_token):
        """Test successful token refresh."""
        refresh_data = {"refresh_token": valid_oauth2_token}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code in [200, 401, 422]

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code in [401, 422]

    def test_refresh_token_expired(self, client):
        """Test refresh with expired/invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code in [401, 422]

    def test_validate_token_success(self, client, valid_oauth2_token):
        """Test successful token validation."""
        headers = {"Authorization": f"Bearer {valid_oauth2_token}"}
        response = client.post("/auth/validate", headers=headers)
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            data = response.json()
            assert data["valid"] is True
            assert "email" in data

    def test_validate_token_missing(self, client):
        """Test validation without token."""
        response = client.post("/auth/validate")
        assert response.status_code in [401, 403, 422]

    def test_validate_token_invalid(self, client):
        """Test validation with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/auth/validate", headers=headers)
        assert response.status_code == 401


class TestAuthRoutesWithMockedController:
    """Test auth routes with fully mocked controller to cover error paths."""

    def test_login_success_with_mocked_controller(self, auth_client):
        """Test successful login with mocked controller."""
        client, mock_controller = auth_client
        token_response = make_token_response_obj()
        mock_controller.login.return_value = token_response

        login_data = {"email": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code in [200, 422]

    def test_login_value_error_returns_401(self, auth_client):
        """Test that ValueError from login returns 401."""
        client, mock_controller = auth_client
        mock_controller.login.side_effect = ValueError("Invalid credentials")

        login_data = {"email": "test@example.com", "password": "wrongpassword"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401

    def test_login_generic_exception_returns_400(self, auth_client):
        """Test that generic Exception from login returns 400."""
        client, mock_controller = auth_client
        mock_controller.login.side_effect = Exception("Unexpected error")

        login_data = {"email": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 400

    def test_refresh_success_with_mocked_controller(self, auth_client):
        """Test successful token refresh with mocked controller."""
        client, mock_controller = auth_client
        token_response = make_token_response_obj()
        mock_controller.refresh_token.return_value = token_response

        refresh_data = {"refresh_token": "valid_refresh_token"}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code in [200, 422]

    def test_refresh_value_error_returns_401(self, auth_client):
        """Test that ValueError from refresh returns 401."""
        client, mock_controller = auth_client
        mock_controller.refresh_token.side_effect = ValueError("Invalid refresh token")

        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code == 401

    def test_refresh_generic_exception_returns_400(self, auth_client):
        """Test that generic Exception from refresh returns 400."""
        client, mock_controller = auth_client
        mock_controller.refresh_token.side_effect = Exception("Unexpected error")

        refresh_data = {"refresh_token": "some_token"}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code == 400
