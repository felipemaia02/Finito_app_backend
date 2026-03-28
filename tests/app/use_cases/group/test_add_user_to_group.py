"""Tests for use_cases/group/add_user_to_group.py"""

import pytest
from app.use_cases.group.add_user_to_group import AddUserToGroupUseCase
from app.domain.dtos.group_dtos import AddUserToGroupInput


class TestAddUserToGroupUseCaseInit:
    def test_init_stores_repository(self, mock_group_repository):
        # Arrange / Act
        use_case = AddUserToGroupUseCase(mock_group_repository)

        # Assert
        assert use_case.repository is mock_group_repository


class TestAddUserToGroupUseCase:
    async def test_add_user_success(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        user_id = "new-user-id"
        group_with_user = sample_group_entity.model_copy(
            update={"user_ids": sample_group_entity.user_ids + [user_id]}
        )
        mock_group_repository.get_by_id.return_value = sample_group_entity
        mock_group_repository.update.return_value = group_with_user
        use_case = AddUserToGroupUseCase(mock_group_repository)
        input_data = AddUserToGroupInput(
            group_id=sample_group_entity.id, user_id=user_id
        )

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is not None
        mock_group_repository.update.assert_called_once()

    async def test_add_user_appends_to_user_ids(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        new_user_id = "brand-new-user"
        mock_group_repository.get_by_id.return_value = sample_group_entity
        mock_group_repository.update.return_value = sample_group_entity
        use_case = AddUserToGroupUseCase(mock_group_repository)
        input_data = AddUserToGroupInput(
            group_id=sample_group_entity.id, user_id=new_user_id
        )

        # Act
        await use_case.execute(input_data)

        # Assert — entity passed to update should include the new user_id
        called_entity = mock_group_repository.update.call_args[0][1]
        assert new_user_id in called_entity.user_ids

    async def test_add_user_group_not_found_returns_none(self, mock_group_repository):
        # Arrange
        mock_group_repository.get_by_id.return_value = None
        use_case = AddUserToGroupUseCase(mock_group_repository)
        input_data = AddUserToGroupInput(group_id="nonexistent", user_id="user1")

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is None
        mock_group_repository.update.assert_not_called()

    async def test_add_user_already_member_raises_value_error(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        existing_user_id = sample_group_entity.user_ids[0]
        mock_group_repository.get_by_id.return_value = sample_group_entity
        use_case = AddUserToGroupUseCase(mock_group_repository)
        input_data = AddUserToGroupInput(
            group_id=sample_group_entity.id, user_id=existing_user_id
        )

        # Act / Assert
        with pytest.raises(ValueError, match="already a member"):
            await use_case.execute(input_data)
        mock_group_repository.update.assert_not_called()

    async def test_add_user_propagates_db_exception(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        mock_group_repository.get_by_id.return_value = sample_group_entity
        mock_group_repository.update.side_effect = RuntimeError("DB error")
        use_case = AddUserToGroupUseCase(mock_group_repository)
        input_data = AddUserToGroupInput(
            group_id=sample_group_entity.id, user_id="new-user"
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await use_case.execute(input_data)
