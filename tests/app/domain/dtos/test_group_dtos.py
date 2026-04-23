"""Tests for domain/dtos/group_dtos.py"""

import pytest
from app.domain.dtos.group_dtos import (
    UpdateGroupInput,
    AddUserToGroupInput,
    RemoveUserFromGroupInput,
)
from app.models.group_schema import GroupUpdate


class TestUpdateGroupInput:
    def test_create_update_group_input(self):
        # Arrange
        group_data = GroupUpdate(group_name="Novo Nome")

        # Act
        dto = UpdateGroupInput(group_id="group123", group_data=group_data)

        # Assert
        assert dto.group_id == "group123"
        assert dto.group_data.group_name == "Novo Nome"

    def test_update_group_input_is_named_tuple(self):
        # Arrange
        group_data = GroupUpdate(group_name="Test")

        # Act
        dto = UpdateGroupInput(group_id="gid", group_data=group_data)

        # Assert — NamedTuples are immutable
        with pytest.raises(AttributeError):
            dto.group_id = "other"

    def test_update_group_input_unpacking(self):
        # Arrange
        group_data = GroupUpdate(group_name="Test")
        dto = UpdateGroupInput(group_id="gid", group_data=group_data)

        # Act
        group_id, gd = dto

        # Assert
        assert group_id == "gid"
        assert gd == group_data


class TestAddUserToGroupInput:
    def test_create_add_user_input(self):
        # Arrange / Act
        dto = AddUserToGroupInput(group_id="group123", user_id="user456")

        # Assert
        assert dto.group_id == "group123"
        assert dto.user_id == "user456"

    def test_add_user_input_is_named_tuple(self):
        # Arrange
        dto = AddUserToGroupInput(group_id="gid", user_id="uid")

        # Act / Assert — immutable
        with pytest.raises(AttributeError):
            dto.group_id = "other"

    def test_add_user_input_unpacking(self):
        # Arrange
        dto = AddUserToGroupInput(group_id="gid", user_id="uid")

        # Act
        group_id, user_id = dto

        # Assert
        assert group_id == "gid"
        assert user_id == "uid"


class TestRemoveUserFromGroupInput:
    def test_create_remove_user_input(self):
        # Arrange / Act
        dto = RemoveUserFromGroupInput(group_id="group123", user_id="user456")

        # Assert
        assert dto.group_id == "group123"
        assert dto.user_id == "user456"

    def test_remove_user_input_is_named_tuple(self):
        # Arrange
        dto = RemoveUserFromGroupInput(group_id="gid", user_id="uid")

        # Act / Assert — immutable
        with pytest.raises(AttributeError):
            dto.user_id = "other"

    def test_remove_user_input_unpacking(self):
        # Arrange
        dto = RemoveUserFromGroupInput(group_id="gid", user_id="uid")

        # Act
        group_id, user_id = dto

        # Assert
        assert group_id == "gid"
        assert user_id == "uid"
