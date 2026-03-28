"""Tests for health check routes."""

import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.infrastructure.settings import get_settings


@pytest.fixture
def client(mock_app_dependencies):
    """Provide test client for API with mocked dependencies."""
    return TestClient(mock_app_dependencies)


@pytest.fixture
def valid_api_key():
    """Provide a valid API key."""
    return get_settings().api_key


class TestHealthRoutes:
    """Test cases for health check endpoints."""

    def test_health_check_success(self, authenticated_client, mocker):
        """Test health check endpoint with valid authentication."""
        # Arrange
        mocker.patch(
            "app.infrastructure.database.database.Database.is_connected",
            return_value=True,
        )
        mock_db = mocker.AsyncMock()
        mock_db.command = mocker.AsyncMock()
        mocker.patch(
            "app.infrastructure.database.database.Database.get_db", return_value=mock_db
        )

        # Act
        response = authenticated_client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert "message" in data

    def test_health_check_response_structure(self, authenticated_client, mocker):
        """Test health check response structure."""
        # Arrange
        mocker.patch(
            "app.infrastructure.database.database.Database.is_connected",
            return_value=True,
        )
        mock_db = mocker.AsyncMock()
        mock_db.command = mocker.AsyncMock()
        mocker.patch(
            "app.infrastructure.database.database.Database.get_db", return_value=mock_db
        )

        # Act
        response = authenticated_client.get("/health")
        data = response.json()

        # Assert
        assert "status" in data
        assert "database" in data
        assert "message" in data

    def test_health_check_with_pending_connection(self, authenticated_client, mocker):
        """Test health check when database is initializing."""
        # Arrange
        mocker.patch(
            "app.infrastructure.database.database.Database.is_connected",
            return_value=False,
        )

        # Act
        response = authenticated_client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "initializing"
        assert data["database"] == "connecting"

    def test_health_check_database_error(self, authenticated_client, mocker):
        """Test health check when database connection fails."""
        # Arrange
        mocker.patch(
            "app.infrastructure.database.database.Database.is_connected",
            return_value=True,
        )
        mock_db = mocker.AsyncMock()
        mock_db.command.side_effect = Exception("Connection failed")
        mocker.patch(
            "app.infrastructure.database.database.Database.get_db", return_value=mock_db
        )

        # Act
        response = authenticated_client.get("/health")

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"
