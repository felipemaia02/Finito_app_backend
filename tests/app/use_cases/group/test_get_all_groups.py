"""Tests for use_cases/group/get_all_groups.py"""

import pytest
from app.use_cases.group.get_all_groups import GetAllGroupsUseCase


class TestGetAllGroupsUseCaseInit:
    def test_init_stores_repository(self, mock_group_repository):
        # Arrange / Act
        use_case = GetAllGroupsUseCase(mock_group_repository)

        # Assert
        assert use_case.repository is mock_group_repository


class TestGetAllGroupsUseCase:
    async def test_get_all_returns_list(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        mock_group_repository.get_all.return_value = [
            sample_group_entity,
            sample_group_entity,
        ]
        use_case = GetAllGroupsUseCase(mock_group_repository)

        # Act
        result = await use_case.execute()

        # Assert
        assert len(result) == 2
        mock_group_repository.get_all.assert_called_once_with(skip=0, limit=100)

    async def test_get_all_empty_list(self, mock_group_repository):
        # Arrange
        mock_group_repository.get_all.return_value = []
        use_case = GetAllGroupsUseCase(mock_group_repository)

        # Act
        result = await use_case.execute()

        # Assert
        assert result == []

    async def test_get_all_passes_pagination(self, mock_group_repository):
        # Arrange
        mock_group_repository.get_all.return_value = []
        use_case = GetAllGroupsUseCase(mock_group_repository)

        # Act
        await use_case.execute(skip=10, limit=5)

        # Assert
        mock_group_repository.get_all.assert_called_once_with(skip=10, limit=5)

    async def test_get_all_propagates_exception(self, mock_group_repository):
        # Arrange
        mock_group_repository.get_all.side_effect = RuntimeError("DB error")
        use_case = GetAllGroupsUseCase(mock_group_repository)

        # Act / Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await use_case.execute()
