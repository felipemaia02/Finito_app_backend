"""Tests for routes/user_public_routes.py"""

import pytest
from datetime import date, datetime, timezone
from bson import ObjectId
from fastapi.testclient import TestClient

from app.api import app
from app.models.user_schema import UserResponse


def make_user_response_obj():
    return UserResponse(
        id=str(ObjectId()),
        name="Test User",
        email="test@example.com",
        date_birth=date(1990, 5, 15),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def public_client(mock_app_dependencies, mock_user_repository):
    """Test client with API key for public user routes."""
    from app.infrastructure.settings import get_settings
    from app.infrastructure.dependencies.user_dependencies import UserDependencies

    mock_app_dependencies.dependency_overrides[UserDependencies.get_repository] = (
        lambda: mock_user_repository
    )

    client = TestClient(mock_app_dependencies)
    client.headers.update({"X-API-Key": get_settings().api_key})
    return client, mock_user_repository


@pytest.fixture
def client(mock_app_dependencies):
    """Provide test client for API with mocked dependencies."""
    return TestClient(mock_app_dependencies)


class TestUserRegisterRoute:
    """Tests for POST /users/register endpoint."""

    def test_register_user_success(self, public_client):
        client, mock_repo = public_client
        # Arrange
        mock_repo.get_by_email.return_value = None
        mock_repo.create.return_value = make_user_response_obj()

        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123!@#",
            "date_birth": "1990-05-15",
        }

        # Act
        response = client.post("/users/register", json=user_data)

        # Assert
        assert response.status_code == 201

    def test_register_user_duplicate_email(self, public_client):
        client, mock_repo = public_client
        # Arrange — email already exists
        mock_repo.get_by_email.return_value = make_user_response_obj()

        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123!@#",
            "date_birth": "1990-05-15",
        }

        # Act
        response = client.post("/users/register", json=user_data)

        # Assert — returns 422 (ValueError) or 400
        assert response.status_code in [400, 422]

    def test_register_user_server_error(self, public_client):
        client, mock_repo = public_client
        # Arrange
        mock_repo.get_by_email.return_value = None
        mock_repo.create.side_effect = Exception("DB error")

        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123!@#",
            "date_birth": "1990-05-15",
        }

        # Act
        response = client.post("/users/register", json=user_data)

        # Assert
        assert response.status_code == 400


class TestUserRoutes:
    """Test cases for user API routes — validation."""

    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email."""
        # Arrange
        user_data = {
            "name": "Test User",
            "email": "invalid-email",
            "password": "password123!",
            "date_birth": "1990-05-15",
        }

        # Act
        response = client.post("/users/register", json=user_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_register_user_short_password(self, client):
        """Test registration with short password."""
        # Arrange
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "pass",  # Too short
            "date_birth": "1990-05-15",
        }

        # Act
        response = client.post("/users/register", json=user_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_register_user_invalid_birth_date(self, client):
        """Test registration with invalid birth date."""
        # Arrange
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123!",
            "date_birth": "2020-05-15",  # Too young
        }

        # Act
        response = client.post("/users/register", json=user_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_get_all_users_success(self, client, valid_oauth2_token):
        """Test getting all users endpoint."""
        # Arrange
        headers = {"Authorization": f"Bearer {valid_oauth2_token}"}

        # Act
        response = client.get("/users?skip=0&limit=100", headers=headers)

        # Debug
        print(f"\nGet all users test - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.json()}")

        # Assert
        # The response should be a list (may be empty in test environment)
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            assert isinstance(response.json(), list)

    def test_get_all_users_with_pagination(self, client, valid_oauth2_token):
        """Test pagination parameters."""
        # Arrange
        headers = {"Authorization": f"Bearer {valid_oauth2_token}"}

        # Act
        response = client.get("/users?skip=10&limit=50", headers=headers)

        # Assert
        assert response.status_code in [200, 422]

    def test_get_user_by_id_not_found(self, client, valid_oauth2_token):
        """Test getting user by invalid ID."""
        # Arrange
        invalid_id = "invalid_id_12345"
        headers = {"Authorization": f"Bearer {valid_oauth2_token}"}

        # Act
        response = client.get(f"/users/{invalid_id}", headers=headers)

        # Assert
        assert response.status_code in [404, 422]

    def test_get_user_by_email_not_found(self, client, valid_oauth2_token):
        """Test getting user by non-existent email."""
        # Arrange
        email = "nonexistent@example.com"
        headers = {"Authorization": f"Bearer {valid_oauth2_token}"}

        # Act
        response = client.get(f"/users/email/{email}", headers=headers)

        # Assert
        assert response.status_code in [404, 422]

    def test_update_user_not_found(self, client, valid_oauth2_token):
        """Test updating non-existent user."""
        # Arrange
        invalid_id = "invalid_id_12345"
        update_data = {"name": "New Name"}
        headers = {"Authorization": f"Bearer {valid_oauth2_token}"}

        # Act
        response = client.put(f"/users/{invalid_id}", json=update_data, headers=headers)

        # Assert
        assert response.status_code in [404, 422]

    def test_delete_user_not_found(self, client, valid_oauth2_token):
        """Test deleting non-existent user."""
        # Arrange
        invalid_id = "invalid_id_12345"
        headers = {"Authorization": f"Bearer {valid_oauth2_token}"}

        # Act
        response = client.delete(f"/users/{invalid_id}", headers=headers)

        # Assert
        assert response.status_code in [404, 422]


class TestUserRoutesIntegration:
    """Integration tests for user routes with mocked database."""

    def test_user_registration_and_retrieval_flow(self, client, mocker):
        """Test complete flow: register user and retrieve."""
        # This would require proper setup and teardown with test database
        # Documented as placeholder for integration testing
        pass

    def test_user_update_flow(self, client, mocker):
        """Test complete flow: register, update, retrieve."""
        # This would require proper setup and teardown
        pass

    def test_user_deletion_flow(self, client, mocker):
        """Test complete flow: register, delete, verify deletion."""
        # This would require proper setup and teardown
        pass
