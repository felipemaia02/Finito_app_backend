"""Tests for domain/entities/group_entity.py"""

import pytest
from pydantic import ValidationError
from app.domain.entities.group_entity import Group


class TestGroupEntityCreation:
    def test_create_group_minimum_fields(self):
        # Arrange / Act
        group = Group(group_name="Viagem")

        # Assert
        assert group.group_name == "Viagem"
        assert group.user_ids == []
        assert group.is_deleted is False
        assert group.id is None
        assert group.created_at is not None
        assert group.updated_at is not None

    def test_create_group_with_all_fields(self, sample_group_data):
        # Arrange / Act
        group = Group(**sample_group_data)

        # Assert
        assert group.group_name == sample_group_data["group_name"]
        assert group.user_ids == sample_group_data["user_ids"]
        assert group.is_deleted is False
        assert group.id == sample_group_data["id"]

    def test_create_group_with_user_ids(self):
        # Arrange / Act
        group = Group(group_name="Turma", user_ids=["id1", "id2", "id3"])

        # Assert
        assert len(group.user_ids) == 3
        assert "id1" in group.user_ids


class TestGroupEntityValidation:
    def test_group_name_required(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            Group()

    def test_group_name_min_length(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            Group(group_name="")

    def test_group_name_max_length(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            Group(group_name="a" * 201)

    def test_group_name_exactly_max_length(self):
        # Arrange / Act
        group = Group(group_name="a" * 200)

        # Assert
        assert len(group.group_name) == 200

    def test_group_name_exactly_min_length(self):
        # Arrange / Act
        group = Group(group_name="A")

        # Assert
        assert group.group_name == "A"


class TestGroupEntityUpdateTimestamp:
    def test_update_timestamp_changes_updated_at(self, sample_group_entity):
        # Arrange
        original_updated_at = sample_group_entity.updated_at

        # Act
        import time
        time.sleep(0.001)
        sample_group_entity.update_timestamp()

        # Assert
        assert sample_group_entity.updated_at > original_updated_at

    def test_update_timestamp_keeps_created_at_unchanged(self, sample_group_entity):
        # Arrange
        original_created_at = sample_group_entity.created_at

        # Act
        sample_group_entity.update_timestamp()

        # Assert
        assert sample_group_entity.created_at == original_created_at


class TestGroupEntityUserIds:
    def test_user_ids_default_empty_list(self):
        # Arrange / Act
        group = Group(group_name="Teste")

        # Assert
        assert group.user_ids == []
        assert isinstance(group.user_ids, list)

    def test_user_ids_are_independent_instances(self):
        # Arrange / Act — two different instances should not share the same list
        group1 = Group(group_name="G1")
        group2 = Group(group_name="G2")
        group1.user_ids.append("user1")

        # Assert
        assert "user1" not in group2.user_ids

    def test_soft_delete_flag_default_false(self):
        # Arrange / Act
        group = Group(group_name="Teste")

        # Assert
        assert group.is_deleted is False

    def test_soft_delete_flag_can_be_set_true(self):
        # Arrange / Act
        group = Group(group_name="Teste", is_deleted=True)

        # Assert
        assert group.is_deleted is True
