"""Tests for use_cases/group/update_group.py"""

import pytest
from app.use_cases.group.update_group import UpdateGroupUseCase
from app.domain.dtos.group_dtos import UpdateGroupInput
from app.models.group_schema import GroupUpdate


class TestUpdateGroupUseCaseInit:
    def test_init_stores_repository(self, mock_group_repository):
        # Arrange / Act
        use_case = UpdateGroupUseCase(mock_group_repository)

        # Assert
        assert use_case.repository is mock_group_repository


class TestUpdateGroupUseCase:
    async def test_update_success(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        updated_entity = sample_group_entity.model_copy(update={"group_name": "Novo Nome"})
        mock_group_repository.get_by_id.return_value = sample_group_entity
        mock_group_repository.update.return_value = updated_entity
        use_case = UpdateGroupUseCase(mock_group_repository)
        input_data = UpdateGroupInput(
            group_id=sample_group_entity.id,
            group_data=GroupUpdate(group_name="Novo Nome"),
        )

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is not None
        mock_group_repository.get_by_id.assert_called_once_with(sample_group_entity.id)
        mock_group_repository.update.assert_called_once()

    async def test_update_applies_new_name(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        mock_group_repository.get_by_id.return_value = sample_group_entity
        mock_group_repository.update.return_value = sample_group_entity
        use_case = UpdateGroupUseCase(mock_group_repository)
        input_data = UpdateGroupInput(
            group_id=sample_group_entity.id,
            group_data=GroupUpdate(group_name="Nome Atualizado"),
        )

        # Act
        await use_case.execute(input_data)

        # Assert — entity passed to update should have new name
        called_entity = mock_group_repository.update.call_args[0][1]
        assert called_entity.group_name == "Nome Atualizado"

    async def test_update_returns_none_when_group_not_found(
        self, mock_group_repository
    ):
        # Arrange
        mock_group_repository.get_by_id.return_value = None
        use_case = UpdateGroupUseCase(mock_group_repository)
        input_data = UpdateGroupInput(
            group_id="nonexistent",
            group_data=GroupUpdate(group_name="Test"),
        )

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is None
        mock_group_repository.update.assert_not_called()

    async def test_update_propagates_exception(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        mock_group_repository.get_by_id.return_value = sample_group_entity
        mock_group_repository.update.side_effect = RuntimeError("DB error")
        use_case = UpdateGroupUseCase(mock_group_repository)
        input_data = UpdateGroupInput(
            group_id=sample_group_entity.id,
            group_data=GroupUpdate(group_name="Test"),
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await use_case.execute(input_data)
