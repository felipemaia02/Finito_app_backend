"""Tests for routes/user_private_routes.py - Protected user endpoint tests."""

import pytest
from datetime import date, datetime, timezone
from bson import ObjectId
from fastapi.testclient import TestClient

from app.models.user_schema import UserResponse
from app.domain.entities.user_entity import User


def make_user_entity(user_id=None):
    oid = user_id or str(ObjectId())
    user = User(
        name="John Silva",
        email="john@example.com",
        password="$2b$12$abcdefghijklmnopqrstuvwxyz1234567890",
        date_birth=date(1990, 5, 15),
    )
    user.id = oid
    return user


def make_user_response_obj(user_id=None):
    oid = user_id or str(ObjectId())
    return UserResponse(
        id=oid,
        name="John Silva",
        email="john@example.com",
        password="$2b$12$abcdefghijklmnopqrstuvwxyz1234567890",
        date_birth=date(1990, 5, 15),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def user_private_client(mock_app_dependencies, mock_user_repository):
    """Test client with API key and OAuth2 token for private user routes."""
    from app.infrastructure.settings import get_settings
    from app.services.oauth2_service import OAuth2Service
    from app.infrastructure.dependencies.user_dependencies import UserDependencies

    oauth2_service = OAuth2Service()
    token, _, _ = oauth2_service.create_token_pair(email="test@example.com")

    mock_app_dependencies.dependency_overrides[UserDependencies.get_repository] = (
        lambda: mock_user_repository
    )

    client = TestClient(mock_app_dependencies)
    client.headers.update(
        {
            "X-API-Key": get_settings().api_key,
            "Authorization": f"Bearer {token}",
        }
    )
    return client, mock_user_repository


class TestUserPrivateGetAllUsers:
    """Test GET /users/ endpoint."""

    def test_get_all_users_empty(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.get_all.return_value = []

        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_users_with_results(self, user_private_client):
        client, mock_repo = user_private_client
        user = make_user_response_obj()
        mock_repo.get_all.return_value = [user]

        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_all_users_with_pagination(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.get_all.return_value = []

        response = client.get("/api/v1/users/?skip=5&limit=20")
        assert response.status_code == 200

    def test_get_all_users_server_error(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.get_all.side_effect = Exception("DB error")

        response = client.get("/api/v1/users/")
        assert response.status_code == 400

    def test_get_all_users_requires_auth(self, mock_app_dependencies):
        from app.infrastructure.settings import get_settings

        client = TestClient(mock_app_dependencies)
        client.headers.update({"X-API-Key": get_settings().api_key})

        response = client.get("/api/v1/users/")
        assert response.status_code in [401, 403, 422]


class TestUserPrivateGetUser:
    """Test GET /users/{user_id} endpoint."""

    def test_get_user_found(self, user_private_client):
        client, mock_repo = user_private_client
        user_id = str(ObjectId())
        user = make_user_response_obj(user_id)
        mock_repo.get_by_id.return_value = user

        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    def test_get_user_not_found(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.get_by_id.return_value = None

        response = client.get(f"/api/v1/users/{str(ObjectId())}")
        assert response.status_code == 404

    def test_get_user_server_error(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.get_by_id.side_effect = Exception("DB error")

        response = client.get(f"/api/v1/users/{str(ObjectId())}")
        assert response.status_code == 400


class TestUserPrivateGetUserByEmail:
    """Test GET /users/email/{email} endpoint."""

    def test_get_user_by_email_found(self, user_private_client):
        client, mock_repo = user_private_client
        email = "john@example.com"
        user = make_user_response_obj()
        mock_repo.get_by_email.return_value = user

        response = client.get(f"/api/v1/users/email/{email}")
        assert response.status_code == 200

    def test_get_user_by_email_not_found(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.get_by_email.return_value = None

        response = client.get("/api/v1/users/email/notfound@example.com")
        assert response.status_code == 404

    def test_get_user_by_email_server_error(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.get_by_email.side_effect = Exception("DB error")

        response = client.get("/api/v1/users/email/error@example.com")
        assert response.status_code == 400


class TestUserPrivateUpdateUser:
    """Test PUT /users/{user_id} endpoint."""

    def test_update_user_success(self, user_private_client):
        client, mock_repo = user_private_client
        user_id = str(ObjectId())
        entity = make_user_entity(user_id)
        make_user_response_obj(user_id)
        mock_repo.get_by_id.return_value = entity
        mock_repo.email_exists.return_value = False
        mock_repo.update.return_value = entity

        update_data = {"name": "Updated Name"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == 200

    def test_update_user_not_found(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.get_by_id.return_value = None
        mock_repo.update.return_value = None

        update_data = {"name": "Updated Name"}
        response = client.put(f"/api/v1/users/{str(ObjectId())}", json=update_data)
        assert response.status_code == 404

    def test_update_user_value_error(self, user_private_client):
        client, mock_repo = user_private_client
        user_id = str(ObjectId())
        user = make_user_response_obj(user_id)
        mock_repo.get_by_id.return_value = user
        mock_repo.email_exists.return_value = True

        update_data = {"email": "taken@example.com"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code in [400, 404]

    def test_update_user_email_conflict_returns_400(self, user_private_client):
        """Test ValueError from email conflict triggers 400 response."""
        from datetime import date
        from copy import deepcopy

        client, mock_repo = user_private_client
        user_id = str(ObjectId())

        # Return a real User entity to avoid AttributeError on update_timestamp()
        entity = User(
            name="John Silva",
            email="john@example.com",
            password="$2b$12$abcdefghijklmnopqrstuvwxyz1234567890",
            date_birth=date(1990, 5, 15),
        )
        entity.id = user_id

        conflicting = User(
            name="Other User",
            email="taken@example.com",
            password="$2b$12$abcdefghijklmnopqrstuvwxyz1234567890",
            date_birth=date(1985, 3, 10),
        )
        conflicting.id = str(ObjectId())

        mock_repo.get_by_id.return_value = entity
        mock_repo.get_by_email.return_value = conflicting  # email conflict

        update_data = {"email": "taken@example.com"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)

        # ValueError caught by route → 400
        assert response.status_code == 400

    def test_update_user_server_error(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.get_by_id.side_effect = Exception("DB error")

        update_data = {"name": "Updated Name"}
        response = client.put(f"/api/v1/users/{str(ObjectId())}", json=update_data)
        assert response.status_code == 400


class TestUserPrivateDeleteUser:
    """Test DELETE /users/{user_id} endpoint."""

    def test_delete_user_success(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.delete.return_value = True

        response = client.delete(f"/api/v1/users/{str(ObjectId())}")
        assert response.status_code == 204

    def test_delete_user_not_found(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.delete.return_value = False

        response = client.delete(f"/api/v1/users/{str(ObjectId())}")
        assert response.status_code == 404

    def test_delete_user_server_error(self, user_private_client):
        client, mock_repo = user_private_client
        mock_repo.delete.side_effect = Exception("DB error")

        response = client.delete(f"/api/v1/users/{str(ObjectId())}")
        assert response.status_code == 400
