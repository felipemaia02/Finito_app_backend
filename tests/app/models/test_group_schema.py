"""Tests for models/group_schema.py"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from app.models.group_schema import GroupCreate, GroupUpdate, GroupResponse, AddUserRequest
from app.models.user_schema import UserResponse
from datetime import date
from bson import ObjectId


class TestGroupCreate:
    def test_create_valid(self):
        # Arrange / Act
        schema = GroupCreate(group_name="Viagem")

        # Assert
        assert schema.group_name == "Viagem"

    def test_group_name_required(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            GroupCreate()

    def test_group_name_empty_string_raises(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            GroupCreate(group_name="")

    def test_group_name_too_long_raises(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            GroupCreate(group_name="x" * 201)

    def test_group_name_max_length_accepted(self):
        # Arrange / Act
        schema = GroupCreate(group_name="x" * 200)

        # Assert
        assert len(schema.group_name) == 200


class TestGroupUpdate:
    def test_all_fields_optional(self):
        # Arrange / Act
        schema = GroupUpdate()

        # Assert
        assert schema.group_name is None

    def test_update_with_new_name(self):
        # Arrange / Act
        schema = GroupUpdate(group_name="Novo Nome")

        # Assert
        assert schema.group_name == "Novo Nome"

    def test_group_name_empty_string_raises(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            GroupUpdate(group_name="")

    def test_group_name_too_long_raises(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            GroupUpdate(group_name="x" * 201)

    def test_model_dump_exclude_unset_returns_empty_when_nothing_set(self):
        # Arrange
        schema = GroupUpdate()

        # Act
        result = schema.model_dump(exclude_unset=True)

        # Assert
        assert result == {}

    def test_model_dump_exclude_unset_returns_only_set_fields(self):
        # Arrange
        schema = GroupUpdate(group_name="Atualizado")

        # Act
        result = schema.model_dump(exclude_unset=True)

        # Assert
        assert result == {"group_name": "Atualizado"}


class TestAddUserRequest:
    def test_create_valid(self):
        # Arrange / Act
        schema = AddUserRequest(user_id="507f1f77bcf86cd799439012")

        # Assert
        assert schema.user_id == "507f1f77bcf86cd799439012"

    def test_user_id_required(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            AddUserRequest()

    def test_user_id_empty_raises(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            AddUserRequest(user_id="")


class TestGroupResponse:
    def _make_user_response(self):
        return UserResponse(
            id=str(ObjectId()),
            name="John Silva",
            email="john@example.com",
            date_birth=date(1990, 5, 15),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    def test_create_valid_response(self):
        # Arrange
        user = self._make_user_response()
        now = datetime.now(timezone.utc)

        # Act
        resp = GroupResponse(
            id=str(ObjectId()),
            group_name="Turma",
            users=[user],
            created_at=now,
            updated_at=now,
        )

        # Assert
        assert resp.group_name == "Turma"
        assert len(resp.users) == 1
        assert resp.users[0].name == "John Silva"

    def test_users_defaults_to_empty_list(self):
        # Arrange
        now = datetime.now(timezone.utc)

        # Act
        resp = GroupResponse(
            id=str(ObjectId()),
            group_name="Turma",
            created_at=now,
            updated_at=now,
        )

        # Assert
        assert resp.users == []

    def test_id_required(self):
        # Arrange / Act / Assert
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError):
            GroupResponse(group_name="Turma", created_at=now, updated_at=now)
