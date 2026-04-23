"""Tests for use_cases/group/create_group.py"""

import pytest
from app.use_cases.group.create_group import CreateGroupUseCase
from app.models.group_schema import GroupCreate


class TestCreateGroupUseCaseInit:
    def test_init_stores_repository(self, mock_group_repository):
        # Arrange / Act
        use_case = CreateGroupUseCase(mock_group_repository)

        # Assert
        assert use_case.repository is mock_group_repository


class TestCreateGroupUseCase:
    async def test_create_success(
        self, mock_group_repository, sample_group_entity, sample_group_create
    ):
        # Arrange
        mock_group_repository.create.return_value = sample_group_entity
        use_case = CreateGroupUseCase(mock_group_repository)

        # Act
        result = await use_case.execute(sample_group_create, creator_user_id="user-123")

        # Assert
        assert result.id == sample_group_entity.id
        assert result.group_name == sample_group_entity.group_name
        mock_group_repository.create.assert_called_once()

    async def test_create_passes_correct_group_name(self, mock_group_repository, sample_group_entity):
        # Arrange
        mock_group_repository.create.return_value = sample_group_entity
        use_case = CreateGroupUseCase(mock_group_repository)
        group_data = GroupCreate(group_name="Meu Grupo Especial")

        # Act
        await use_case.execute(group_data, creator_user_id="user-123")

        # Assert — verify group passed to create has the correct name
        called_arg = mock_group_repository.create.call_args[0][0]
        assert called_arg.group_name == "Meu Grupo Especial"

    async def test_create_adds_creator_to_user_ids(self, mock_group_repository, sample_group_entity):
        # Arrange
        mock_group_repository.create.return_value = sample_group_entity
        use_case = CreateGroupUseCase(mock_group_repository)
        group_data = GroupCreate(group_name="Novo Grupo")
        creator_id = "creator-user-id"

        # Act
        await use_case.execute(group_data, creator_user_id=creator_id)

        # Assert — creator must be in user_ids
        called_arg = mock_group_repository.create.call_args[0][0]
        assert creator_id in called_arg.user_ids

    async def test_create_propagates_exception(
        self, mock_group_repository, sample_group_create
    ):
        # Arrange
        mock_group_repository.create.side_effect = RuntimeError("DB error")
        use_case = CreateGroupUseCase(mock_group_repository)

        # Act / Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await use_case.execute(sample_group_create, creator_user_id="user-123")
