"""Tests for use_cases/group/remove_user_from_group.py"""

import pytest
from app.use_cases.group.remove_user_from_group import RemoveUserFromGroupUseCase
from app.domain.dtos.group_dtos import RemoveUserFromGroupInput


class TestRemoveUserFromGroupUseCaseInit:
    def test_init_stores_repository(self, mock_group_repository):
        # Arrange / Act
        use_case = RemoveUserFromGroupUseCase(mock_group_repository)

        # Assert
        assert use_case.repository is mock_group_repository


class TestRemoveUserFromGroupUseCase:
    async def test_remove_user_success(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        user_to_remove = sample_group_entity.user_ids[0]
        remaining_ids = [u for u in sample_group_entity.user_ids if u != user_to_remove]
        group_after_removal = sample_group_entity.model_copy(
            update={"user_ids": remaining_ids}
        )
        mock_group_repository.get_by_id.return_value = sample_group_entity
        mock_group_repository.update.return_value = group_after_removal
        use_case = RemoveUserFromGroupUseCase(mock_group_repository)
        input_data = RemoveUserFromGroupInput(
            group_id=sample_group_entity.id, user_id=user_to_remove
        )

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is not None
        mock_group_repository.update.assert_called_once()

    async def test_remove_user_removes_from_user_ids(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        user_to_remove = sample_group_entity.user_ids[0]
        mock_group_repository.get_by_id.return_value = sample_group_entity
        mock_group_repository.update.return_value = sample_group_entity
        use_case = RemoveUserFromGroupUseCase(mock_group_repository)
        input_data = RemoveUserFromGroupInput(
            group_id=sample_group_entity.id, user_id=user_to_remove
        )

        # Act
        await use_case.execute(input_data)

        # Assert — entity passed to update should NOT contain the removed user
        called_entity = mock_group_repository.update.call_args[0][1]
        assert user_to_remove not in called_entity.user_ids

    async def test_remove_user_group_not_found_returns_none(
        self, mock_group_repository
    ):
        # Arrange
        mock_group_repository.get_by_id.return_value = None
        use_case = RemoveUserFromGroupUseCase(mock_group_repository)
        input_data = RemoveUserFromGroupInput(group_id="nonexistent", user_id="user1")

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is None
        mock_group_repository.update.assert_not_called()

    async def test_remove_user_not_member_raises_value_error(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        mock_group_repository.get_by_id.return_value = sample_group_entity
        use_case = RemoveUserFromGroupUseCase(mock_group_repository)
        input_data = RemoveUserFromGroupInput(
            group_id=sample_group_entity.id, user_id="user-not-in-group"
        )

        # Act / Assert
        with pytest.raises(ValueError, match="not a member"):
            await use_case.execute(input_data)
        mock_group_repository.update.assert_not_called()

    async def test_remove_user_propagates_db_exception(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        user_to_remove = sample_group_entity.user_ids[0]
        mock_group_repository.get_by_id.return_value = sample_group_entity
        mock_group_repository.update.side_effect = RuntimeError("DB error")
        use_case = RemoveUserFromGroupUseCase(mock_group_repository)
        input_data = RemoveUserFromGroupInput(
            group_id=sample_group_entity.id, user_id=user_to_remove
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await use_case.execute(input_data)
