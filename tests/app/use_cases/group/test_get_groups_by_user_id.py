"""Tests for use_cases/group/get_groups_by_user_id.py"""

import pytest
from app.use_cases.group.get_groups_by_user_id import GetGroupsByUserIdUseCase


class TestGetGroupsByUserIdUseCaseInit:
    def test_init_stores_repository(self, mock_group_repository):
        # Arrange / Act
        use_case = GetGroupsByUserIdUseCase(mock_group_repository)

        # Assert
        assert use_case.repository is mock_group_repository


class TestGetGroupsByUserIdUseCase:
    async def test_returns_groups_for_user(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        mock_group_repository.get_by_user_id.return_value = [sample_group_entity]
        use_case = GetGroupsByUserIdUseCase(mock_group_repository)

        # Act
        result = await use_case.execute("user-123")

        # Assert
        assert len(result) == 1
        assert result[0].id == sample_group_entity.id
        mock_group_repository.get_by_user_id.assert_called_once_with("user-123")

    async def test_returns_empty_list_when_no_groups(self, mock_group_repository):
        # Arrange
        mock_group_repository.get_by_user_id.return_value = []
        use_case = GetGroupsByUserIdUseCase(mock_group_repository)

        # Act
        result = await use_case.execute("user-with-no-groups")

        # Assert
        assert result == []

    async def test_propagates_exception(self, mock_group_repository):
        # Arrange
        mock_group_repository.get_by_user_id.side_effect = RuntimeError("DB error")
        use_case = GetGroupsByUserIdUseCase(mock_group_repository)

        # Act / Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await use_case.execute("user-123")
