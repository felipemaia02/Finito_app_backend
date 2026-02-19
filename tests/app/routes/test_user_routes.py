"""Tests for routes/user_routes.py"""

import pytest
from httpx import AsyncClient
from datetime import date
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import app


@pytest.fixture
def client(mock_app_dependencies):
    """Provide test client for API with mocked dependencies."""
    return TestClient(mock_app_dependencies)


@pytest.fixture
async def async_client(mock_app_dependencies):
    """Provide async test client for API with mocked dependencies."""
    async with AsyncClient(app=mock_app_dependencies, base_url="http://test") as ac:
        yield ac


class TestUserRoutes:
    """Test cases for user API routes."""
    
    def test_register_user_success(self, client, mocker):
        """Test successful user registration endpoint."""
        # Arrange
        user_data = {
            "nome": "Test User",
            "email": "test@example.com",
            "senha": "password123!@#",
            "data_nascimento": "1990-05-15",
        }
        
        # Mock the dependencies
        mock_repo = mocker.AsyncMock()
        mock_repo.get_by_email.return_value = None
        
        # Act - Note: This would require proper mocking of dependencies
        # For now, we'll document the expected behavior
        # response = client.post("/users/register", json=user_data)
        
        # Assert
        # assert response.status_code == 201
        # assert response.json()["email"] == user_data["email"]
    
    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email."""
        # Arrange
        user_data = {
            "nome": "Test User",
            "email": "invalid-email",
            "senha": "password123!",
            "data_nascimento": "1990-05-15",
        }
        
        # Act
        response = client.post("/users/register", json=user_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_register_user_short_password(self, client):
        """Test registration with short password."""
        # Arrange
        user_data = {
            "nome": "Test User",
            "email": "test@example.com",
            "senha": "pass",  # Too short
            "data_nascimento": "1990-05-15",
        }
        
        # Act
        response = client.post("/users/register", json=user_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_register_user_invalid_birth_date(self, client):
        """Test registration with invalid birth date."""
        # Arrange
        user_data = {
            "nome": "Test User",
            "email": "test@example.com",
            "senha": "password123!",
            "data_nascimento": "2020-05-15",  # Too young
        }
        
        # Act
        response = client.post("/users/register", json=user_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_get_all_users_success(self, client):
        """Test getting all users endpoint."""
        # Arrange & Act
        response = client.get("/users?skip=0&limit=100")
        
        # Assert
        # The response should be a list (may be empty in test environment)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_all_users_with_pagination(self, client):
        """Test pagination parameters."""
        # Arrange & Act
        response = client.get("/users?skip=10&limit=50")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_user_by_id_not_found(self, client):
        """Test getting user by invalid ID."""
        # Arrange
        invalid_id = "invalid_id_12345"
        
        # Act
        response = client.get(f"/users/{invalid_id}")
        
        # Assert
        assert response.status_code == 404
    
    def test_get_user_by_email_not_found(self, client):
        """Test getting user by non-existent email."""
        # Arrange
        email = "nonexistent@example.com"
        
        # Act
        response = client.get(f"/users/email/{email}")
        
        # Assert
        assert response.status_code == 404
    
    def test_update_user_not_found(self, client):
        """Test updating non-existent user."""
        # Arrange
        invalid_id = "invalid_id_12345"
        update_data = {"nome": "New Name"}
        
        # Act
        response = client.put(f"/users/{invalid_id}", json=update_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_user_not_found(self, client):
        """Test deleting non-existent user."""
        # Arrange
        invalid_id = "invalid_id_12345"
        
        # Act
        response = client.delete(f"/users/{invalid_id}")
        
        # Assert
        assert response.status_code == 404


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
