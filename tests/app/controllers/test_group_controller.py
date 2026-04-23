"""Tests for controllers/group_controller.py"""

from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, date
from bson import ObjectId

from app.controllers.group_controller import GroupController
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.entities.group_entity import Group
from app.domain.entities.user_entity import User
from app.models.group_schema import GroupCreate, GroupUpdate, GroupResponse


def make_group_repo():
    return AsyncMock(spec=IGroupRepository)


def make_user_repo():
    return AsyncMock(spec=IUserRepository)


def make_group(user_ids=None, creator_id=None):
    return Group(
        id=str(ObjectId()),
        group_name="Grupo Teste",
        creator_id=creator_id or str(ObjectId()),
        user_ids=user_ids or [],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_user():
    return User(
        id=str(ObjectId()),
        name="John Silva",
        email="john@example.com",
        password="$2b$12$hashed",
        date_birth=date(1990, 5, 15),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


class TestGroupControllerInit:
    def test_controller_creation(self):
        # Arrange / Act
        controller = GroupController(make_group_repo(), make_user_repo())

        # Assert
        assert controller is not None

    def test_controller_has_all_use_cases(self):
        # Arrange / Act
        controller = GroupController(make_group_repo(), make_user_repo())

        # Assert
        assert controller.create_group_use_case is not None
        assert controller.get_all_groups_use_case is not None
        assert controller.get_group_by_id_use_case is not None
        assert controller.update_group_use_case is not None
        assert controller.delete_group_use_case is not None
        assert controller.add_user_to_group_use_case is not None
        assert controller.remove_user_from_group_use_case is not None


class TestGroupControllerBuildResponse:
    async def test_build_response_populates_users(self):
        # Arrange
        user = make_user()
        group = make_group(user_ids=[user.id])
        user_repo = make_user_repo()
        user_repo.get_by_id.return_value = user
        controller = GroupController(make_group_repo(), user_repo)

        # Act
        response = await controller._build_response(group)

        # Assert
        assert isinstance(response, GroupResponse)
        assert len(response.users) == 1
        assert response.users[0].name == user.name

    async def test_build_response_skips_missing_users(self):
        # Arrange
        group = make_group(user_ids=["nonexistent-id"])
        user_repo = make_user_repo()
        user_repo.get_by_id.return_value = None  # user not found
        controller = GroupController(make_group_repo(), user_repo)

        # Act
        response = await controller._build_response(group)

        # Assert
        assert response.users == []

    async def test_build_response_empty_user_ids(self):
        # Arrange
        group = make_group(user_ids=[])
        controller = GroupController(make_group_repo(), make_user_repo())

        # Act
        response = await controller._build_response(group)

        # Assert
        assert response.users == []


class TestGroupControllerCreateGroup:
    async def test_create_group_delegates_and_returns_response(self):
        # Arrange
        creator = make_user()
        group = make_group(user_ids=[creator.id])
        group_repo = make_group_repo()
        user_repo = make_user_repo()
        user_repo.get_by_email.return_value = creator
        user_repo.get_by_id.return_value = creator
        controller = GroupController(group_repo, user_repo)

        with patch.object(
            controller.create_group_use_case, "execute", new=AsyncMock(return_value=group)
        ):
            # Act
            result = await controller.create_group(GroupCreate(group_name="Grupo"), creator_email="creator@example.com")

        # Assert
        assert isinstance(result, GroupResponse)
        assert result.group_name == group.group_name

    async def test_create_group_passes_creator_user_id(self):
        # Arrange
        creator = make_user()
        group = make_group(user_ids=[creator.id])
        group_repo = make_group_repo()
        user_repo = make_user_repo()
        user_repo.get_by_email.return_value = creator
        user_repo.get_by_id.return_value = creator
        controller = GroupController(group_repo, user_repo)
        execute_mock = AsyncMock(return_value=group)

        with patch.object(controller.create_group_use_case, "execute", new=execute_mock):
            # Act
            await controller.create_group(GroupCreate(group_name="Grupo"), creator_email="creator@example.com")

        # Assert — creator user id must be passed to use case
        execute_mock.assert_called_once()
        assert execute_mock.call_args[0][1] == creator.id

    async def test_create_group_creator_not_found_passes_none(self):
        # Arrange
        group = make_group()
        group_repo = make_group_repo()
        user_repo = make_user_repo()
        user_repo.get_by_email.return_value = None
        controller = GroupController(group_repo, user_repo)
        execute_mock = AsyncMock(return_value=group)

        with patch.object(controller.create_group_use_case, "execute", new=execute_mock):
            # Act
            await controller.create_group(GroupCreate(group_name="Grupo"), creator_email="unknown@example.com")

        # Assert — None passed when user not found
        assert execute_mock.call_args[0][1] is None


class TestGroupControllerGetAllGroups:
    async def test_get_all_groups_returns_list(self):
        # Arrange
        groups = [make_group(), make_group()]
        user = make_user()
        user_repo = make_user_repo()
        user_repo.get_by_email.return_value = user
        user_repo.get_by_id.return_value = None
        controller = GroupController(make_group_repo(), user_repo)

        with patch.object(
            controller.get_groups_by_user_id_use_case,
            "execute",
            new=AsyncMock(return_value=groups),
        ):
            # Act
            result = await controller.get_all_groups("test@example.com")

        # Assert
        assert len(result) == 2
        assert all(isinstance(r, GroupResponse) for r in result)

    async def test_get_all_groups_empty(self):
        # Arrange
        user = make_user()
        user_repo = make_user_repo()
        user_repo.get_by_email.return_value = user
        user_repo.get_by_id.return_value = None
        controller = GroupController(make_group_repo(), user_repo)

        with patch.object(
            controller.get_groups_by_user_id_use_case,
            "execute",
            new=AsyncMock(return_value=[]),
        ):
            # Act
            result = await controller.get_all_groups("test@example.com")

        # Assert
        assert result == []


class TestGroupControllerGetGroupById:
    async def test_get_group_by_id_found(self):
        # Arrange
        group = make_group()
        controller = GroupController(make_group_repo(), make_user_repo())

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=group),
        ), patch.object(controller, "_require_membership", new=AsyncMock(return_value=None)):
            # Act
            result = await controller.get_group_by_id(group.id, "test@example.com")

        # Assert
        assert isinstance(result, GroupResponse)

    async def test_get_group_by_id_not_found_returns_none(self):
        # Arrange
        controller = GroupController(make_group_repo(), make_user_repo())

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=None),
        ):
            # Act
            result = await controller.get_group_by_id("nonexistent", "test@example.com")

        # Assert
        assert result is None


class TestGroupControllerUpdateGroup:
    async def test_update_group_found(self):
        # Arrange
        group = make_group()
        controller = GroupController(make_group_repo(), make_user_repo())

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=group),
        ), patch.object(
            controller.update_group_use_case,
            "execute",
            new=AsyncMock(return_value=group),
        ), patch.object(controller, "_require_membership", new=AsyncMock(return_value=None)):
            # Act
            result = await controller.update_group(group.id, GroupUpdate(group_name="Novo"), "test@example.com")

        # Assert
        assert isinstance(result, GroupResponse)

    async def test_update_group_not_found_returns_none(self):
        # Arrange
        controller = GroupController(make_group_repo(), make_user_repo())

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=None),
        ):
            # Act
            result = await controller.update_group("nonexistent", GroupUpdate(group_name="X"), "test@example.com")

        # Assert
        assert result is None


class TestGroupControllerDeleteGroup:
    async def test_delete_group_success(self):
        # Arrange
        user = make_user()
        group = make_group(creator_id=user.id)
        user_repo = make_user_repo()
        user_repo.get_by_email.return_value = user
        controller = GroupController(make_group_repo(), user_repo)

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=group),
        ), patch.object(
            controller.delete_group_use_case,
            "execute",
            new=AsyncMock(return_value=True),
        ):
            # Act
            result = await controller.delete_group("group-id", user.email)

        # Assert
        assert result is True

    async def test_delete_group_not_found(self):
        # Arrange
        controller = GroupController(make_group_repo(), make_user_repo())

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=None),
        ):
            # Act
            result = await controller.delete_group("nonexistent", "test@example.com")

        # Assert
        assert result is False


class TestGroupControllerAddUser:
    async def test_add_user_to_group_success(self):
        # Arrange
        group = make_group(user_ids=["user1"])
        user_repo = make_user_repo()
        user_repo.get_by_id.return_value = None  # no users to populate in response
        controller = GroupController(make_group_repo(), user_repo)

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=group),
        ), patch.object(
            controller.add_user_to_group_use_case,
            "execute",
            new=AsyncMock(return_value=group),
        ), patch.object(controller, "_require_membership", new=AsyncMock(return_value=None)):
            # Act
            result = await controller.add_user_to_group("group-id", "user1", "test@example.com")

        # Assert
        assert isinstance(result, GroupResponse)

    async def test_add_user_group_not_found_returns_none(self):
        # Arrange
        controller = GroupController(make_group_repo(), make_user_repo())

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=None),
        ):
            # Act
            result = await controller.add_user_to_group("nonexistent", "user1", "test@example.com")

        # Assert
        assert result is None


class TestGroupControllerRemoveUser:
    async def test_remove_user_from_group_success(self):
        # Arrange
        group = make_group()
        controller = GroupController(make_group_repo(), make_user_repo())

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=group),
        ), patch.object(
            controller.remove_user_from_group_use_case,
            "execute",
            new=AsyncMock(return_value=group),
        ), patch.object(controller, "_require_membership", new=AsyncMock(return_value=None)):
            # Act
            result = await controller.remove_user_from_group("group-id", "user1", "test@example.com")

        # Assert
        assert isinstance(result, GroupResponse)

    async def test_remove_user_group_not_found_returns_none(self):
        # Arrange
        controller = GroupController(make_group_repo(), make_user_repo())

        with patch.object(
            controller.get_group_by_id_use_case,
            "execute",
            new=AsyncMock(return_value=None),
        ):
            # Act
            result = await controller.remove_user_from_group("nonexistent", "user1", "test@example.com")

        # Assert
        assert result is None


class TestGroupControllerGetGroupsByUserEmail:
    async def test_returns_groups_for_existing_user(self):
        # Arrange
        user = make_user()
        groups = [make_group(user_ids=[user.id]), make_group(user_ids=[user.id])]
        user_repo = make_user_repo()
        user_repo.get_by_email.return_value = user
        user_repo.get_by_id.return_value = None  # no user population in response
        controller = GroupController(make_group_repo(), user_repo)

        with patch.object(
            controller.get_groups_by_user_id_use_case,
            "execute",
            new=AsyncMock(return_value=groups),
        ):
            # Act
            result = await controller.get_groups_by_user_email("user@example.com")

        # Assert
        assert len(result) == 2
        assert all(isinstance(r, GroupResponse) for r in result)

    async def test_returns_empty_list_when_user_not_found(self):
        # Arrange
        user_repo = make_user_repo()
        user_repo.get_by_email.return_value = None
        controller = GroupController(make_group_repo(), user_repo)

        # Act
        result = await controller.get_groups_by_user_email("unknown@example.com")

        # Assert
        assert result == []
