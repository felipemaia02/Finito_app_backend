"""Tests for routes/group_routes.py — HTTP endpoint tests."""

import pytest
from datetime import datetime, timezone, date
from bson import ObjectId
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.api import app
from app.models.group_schema import GroupResponse
from app.domain.entities.user_entity import User
from app.domain.entities.group_entity import Group
from app.domain.interfaces.user_repository_interface import IUserRepository


def make_group_response(group_id=None, user_ids=None):
    oid = group_id or str(ObjectId())
    return GroupResponse(
        id=oid,
        group_name="Viagem Europa 2026",
        users=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_test_user(user_id=None):
    uid = user_id or str(ObjectId())
    return User(
        id=uid,
        name="Test User",
        email="test@example.com",
        password="$2b$12$hashed",
        date_birth=date(1990, 1, 1),
        is_active=True,
    )


@pytest.fixture
def group_client(mock_group_repository, mock_user_repository):
    """Test client with API key and OAuth2 token for group routes."""
    from app.infrastructure.settings import get_settings
    from app.services.oauth2_service import OAuth2Service
    from app.infrastructure.dependencies.group_dependencies import GroupDependencies

    oauth2_service = OAuth2Service()
    token, _, _ = oauth2_service.create_token_pair(email="test@example.com")

    overrides = app.dependency_overrides.copy()
    app.dependency_overrides[GroupDependencies.get_group_repository] = (
        lambda: mock_group_repository
    )
    app.dependency_overrides[GroupDependencies.get_user_repository] = (
        lambda: mock_user_repository
    )

    client = TestClient(app)
    client.headers.update(
        {
            "X-API-Key": get_settings().api_key,
            "Authorization": f"Bearer {token}",
        }
    )
    yield client, mock_group_repository, mock_user_repository

    app.dependency_overrides = overrides


class TestGroupRouterInit:
    def test_router_exists(self):
        # Arrange / Act / Assert
        from app.routes.group_routes import router

        assert router is not None

    def test_router_has_routes(self):
        # Arrange / Act / Assert
        from app.routes.group_routes import router

        assert len(router.routes) > 0


class TestCreateGroupRoute:
    def test_create_group_success(self, group_client):
        # Arrange
        client, mock_repo, mock_user_repo = group_client

        user_id = str(ObjectId())
        creator = make_test_user(user_id)
        mock_user_repo.get_by_email.return_value = creator
        mock_user_repo.get_by_id.return_value = None

        group_entity = Group(
            id=str(ObjectId()),
            group_name="Viagem Europa 2026",
            creator_id=user_id,
            user_ids=[user_id],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.create.return_value = group_entity

        # Act
        response = client.post("/api/v1/groups", json={"group_name": "Viagem Europa 2026"})

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Group created successfully"

    def test_create_group_missing_name_returns_422(self, group_client):
        # Arrange
        client, _, _ = group_client

        # Act
        response = client.post("/api/v1/groups", json={})

        # Assert
        assert response.status_code == 422

    def test_create_group_empty_name_returns_422(self, group_client):
        # Arrange
        client, _, _ = group_client

        # Act
        response = client.post("/api/v1/groups", json={"group_name": ""})

        # Assert
        assert response.status_code == 422

    def test_create_group_db_error_returns_400(self, group_client):
        # Arrange
        client, mock_repo, mock_user_repo = group_client
        mock_user_repo.get_by_email.return_value = make_test_user()
        mock_repo.create.side_effect = RuntimeError("DB failure")

        # Act
        response = client.post("/api/v1/groups", json={"group_name": "Test"})

        # Assert
        assert response.status_code == 400


# class TestListAllGroupsRoute:
#     def test_list_groups_success(self, group_client):
#         # Arrange
#         client, mock_repo, mock_user_repo = group_client
#         user_id = str(ObjectId())

#         groups = [
#             Group(
#                 id=str(ObjectId()),
#                 group_name=f"Grupo {i}",
#                 creator_id=user_id,
#                 user_ids=[],
#                 created_at=datetime.now(timezone.utc),
#                 updated_at=datetime.now(timezone.utc),
#             )
#             for i in range(3)
#         ]
#         mock_repo.get_all.return_value = groups
#         mock_user_repo.get_by_id.return_value = None

#         # Act
#         response = client.get("/api/v1/groups")

#         # Assert
#         assert response.status_code == 200
#         assert len(response.json()) == 3

#     def test_list_groups_empty(self, group_client):
#         # Arrange
#         client, mock_repo, _ = group_client
#         mock_repo.get_all.return_value = []

#         # Act
#         response = client.get("/api/v1/groups")

#         # Assert
#         assert response.status_code == 200
#         assert response.json() == []

#     def test_list_groups_with_pagination(self, group_client):
#         # Arrange
#         client, mock_repo, _ = group_client
#         mock_repo.get_all.return_value = []

#         # Act
#         response = client.get("/api/v1/groups?skip=10&limit=5")

#         # Assert
#         assert response.status_code == 200


class TestGetGroupByIdRoute:
    def test_get_group_found(self, group_client):
        # Arrange
        client, mock_repo, mock_user_repo = group_client

        group_id = str(ObjectId())
        user_id = str(ObjectId())

        auth_user = make_test_user(user_id)
        mock_user_repo.get_by_email.return_value = auth_user
        mock_user_repo.get_by_id.return_value = None

        group = Group(
            id=group_id,
            group_name="Turma",
            creator_id=user_id,
            user_ids=[user_id],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.get_by_id.return_value = group

        # Act
        response = client.get(f"/api/v1/groups/{group_id}")

        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == group_id

    def test_get_group_not_found_returns_404(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.return_value = None

        # Act
        response = client.get(f"/api/v1/groups/{str(ObjectId())}")

        # Assert
        assert response.status_code == 404


class TestUpdateGroupRoute:
    def test_update_group_success(self, group_client):
        # Arrange
        client, mock_repo, mock_user_repo = group_client

        group_id = str(ObjectId())
        user_id = str(ObjectId())

        auth_user = make_test_user(user_id)
        mock_user_repo.get_by_email.return_value = auth_user
        mock_user_repo.get_by_id.return_value = None

        group = Group(
            id=group_id,
            group_name="Nome Atualizado",
            creator_id=user_id,
            user_ids=[user_id],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.get_by_id.return_value = group
        mock_repo.update.return_value = group

        # Act
        response = client.patch(f"/api/v1/groups/{group_id}", json={"group_name": "Nome Atualizado"})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == "Group updated successfully"

    def test_update_group_not_found_returns_404(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.return_value = None

        # Act
        response = client.patch(f"/api/v1/groups/{str(ObjectId())}", json={"group_name": "Test"})

        # Assert
        assert response.status_code == 404


class TestDeleteGroupRoute:
    def test_delete_group_success(self, group_client):
        # Arrange
        client, mock_repo, mock_user_repo = group_client

        group_id = str(ObjectId())
        user_id = str(ObjectId())

        auth_user = make_test_user(user_id)
        mock_user_repo.get_by_email.return_value = auth_user

        group = Group(
            id=group_id,
            group_name="Test Group",
            creator_id=user_id,
            user_ids=[user_id],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.get_by_id.return_value = group
        mock_repo.delete.return_value = True

        # Act
        response = client.delete(f"/api/v1/groups/{group_id}")

        # Assert
        assert response.status_code == 204

    def test_delete_group_not_found_returns_404(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.return_value = None

        # Act
        response = client.delete(f"/api/v1/groups/{str(ObjectId())}")

        # Assert
        assert response.status_code == 404


class TestAddUserToGroupRoute:
    def test_add_user_success(self, group_client):
        # Arrange
        client, mock_repo, mock_user_repo = group_client

        group_id = str(ObjectId())
        existing_user_id = str(ObjectId())
        new_user_id = str(ObjectId())

        auth_user = make_test_user(existing_user_id)
        mock_user_repo.get_by_email.return_value = auth_user
        mock_user_repo.get_by_id.return_value = None

        group_before = Group(
            id=group_id,
            group_name="Turma",
            creator_id=existing_user_id,
            user_ids=[existing_user_id],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        group_after = Group(
            id=group_id,
            group_name="Turma",
            creator_id=existing_user_id,
            user_ids=[existing_user_id, new_user_id],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.get_by_id.return_value = group_before
        mock_repo.update.return_value = group_after

        # Act
        response = client.post(
            f"/api/v1/groups/{group_id}/users", json={"user_id": new_user_id}
        )

        # Assert
        assert response.status_code == 200

    def test_add_user_group_not_found_returns_404(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.return_value = None

        # Act
        response = client.post(
            f"/api/v1/groups/{str(ObjectId())}/users",
            json={"user_id": str(ObjectId())},
        )

        # Assert
        assert response.status_code == 404

    def test_add_user_already_member_returns_422(self, group_client):
        # Arrange
        client, mock_repo, mock_user_repo = group_client

        group_id = str(ObjectId())
        auth_user_id = str(ObjectId())
        user_to_add_id = str(ObjectId())

        auth_user = make_test_user(auth_user_id)
        mock_user_repo.get_by_email.return_value = auth_user

        group = Group(
            id=group_id,
            group_name="Turma",
            creator_id=auth_user_id,
            user_ids=[auth_user_id, user_to_add_id],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.get_by_id.return_value = group

        # Act
        response = client.post(
            f"/api/v1/groups/{group_id}/users", json={"user_id": user_to_add_id}
        )

        # Assert
        assert response.status_code == 422


class TestRemoveUserFromGroupRoute:
    def test_remove_user_success(self, group_client):
        # Arrange
        client, mock_repo, mock_user_repo = group_client

        group_id = str(ObjectId())
        auth_user_id = str(ObjectId())
        user_to_remove_id = str(ObjectId())

        auth_user = make_test_user(auth_user_id)
        mock_user_repo.get_by_email.return_value = auth_user
        mock_user_repo.get_by_id.return_value = None

        group_before = Group(
            id=group_id,
            group_name="Turma",
            creator_id=auth_user_id,
            user_ids=[auth_user_id, user_to_remove_id],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        group_after = Group(
            id=group_id,
            group_name="Turma",
            creator_id=auth_user_id,
            user_ids=[auth_user_id],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.get_by_id.return_value = group_before
        mock_repo.update.return_value = group_after

        # Act
        response = client.delete(f"/api/v1/groups/{group_id}/users/{user_to_remove_id}")

        # Assert
        assert response.status_code == 200

    def test_remove_user_group_not_found_returns_404(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.return_value = None

        # Act
        response = client.delete(
            f"/api/v1/groups/{str(ObjectId())}/users/{str(ObjectId())}"
        )

        # Assert
        assert response.status_code == 404

    def test_remove_user_not_member_returns_422(self, group_client):
        # Arrange
        client, mock_repo, mock_user_repo = group_client

        group_id = str(ObjectId())
        auth_user_id = str(ObjectId())
        user_to_remove_id = str(ObjectId())

        auth_user = make_test_user(auth_user_id)
        mock_user_repo.get_by_email.return_value = auth_user

        group = Group(
            id=group_id,
            group_name="Turma",
            creator_id=auth_user_id,
            user_ids=[auth_user_id],  # user_to_remove_id NOT in list
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.get_by_id.return_value = group

        # Act
        response = client.delete(f"/api/v1/groups/{group_id}/users/{user_to_remove_id}")

        # Assert
        assert response.status_code == 422


class TestGroupRouteExceptionHandlers:
    """Test generic exception (non-HTTP, non-ValueError) handlers in each route."""

    # def test_list_groups_generic_exception_returns_400(self, group_client):
    #     # Arrange
    #     client, mock_repo, _ = group_client
    #     mock_repo.get_all.side_effect = RuntimeError("unexpected DB error")

    #     # Act
    #     response = client.get("/api/v1/groups")

    #     # Assert
    #     assert response.status_code == 400

    def test_get_group_generic_exception_returns_400(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.side_effect = RuntimeError("unexpected DB error")

        # Act
        response = client.get(f"/api/v1/groups/{str(ObjectId())}")

        # Assert
        assert response.status_code == 400

    def test_update_group_generic_exception_returns_400(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.side_effect = RuntimeError("unexpected DB error")

        # Act
        response = client.patch(f"/api/v1/groups/{str(ObjectId())}", json={"group_name": "X"})

        # Assert
        assert response.status_code == 400

    def test_update_group_value_error_returns_422(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.side_effect = ValueError("invalid group data")

        # Act
        response = client.patch(f"/api/v1/groups/{str(ObjectId())}", json={"group_name": "X"})

        # Assert
        assert response.status_code == 422

    def test_delete_group_generic_exception_returns_400(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.side_effect = RuntimeError("unexpected DB error")

        # Act
        response = client.delete(f"/api/v1/groups/{str(ObjectId())}")

        # Assert
        assert response.status_code == 400

    def test_add_user_generic_exception_returns_400(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.side_effect = RuntimeError("unexpected DB error")

        # Act
        response = client.post(
            f"/api/v1/groups/{str(ObjectId())}/users", json={"user_id": str(ObjectId())}
        )

        # Assert
        assert response.status_code == 400

    def test_remove_user_generic_exception_returns_400(self, group_client):
        # Arrange
        client, mock_repo, _ = group_client
        mock_repo.get_by_id.side_effect = RuntimeError("unexpected DB error")

        # Act
        response = client.delete(
            f"/api/v1/groups/{str(ObjectId())}/users/{str(ObjectId())}"
        )

        # Assert
        assert response.status_code == 400
