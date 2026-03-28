"""Tests for use_cases/group/get_group_by_id.py"""

import pytest
from app.use_cases.group.get_group_by_id import GetGroupByIdUseCase


class TestGetGroupByIdUseCaseInit:
    def test_init_stores_repository(self, mock_group_repository):
        # Arrange / Act
        use_case = GetGroupByIdUseCase(mock_group_repository)

        # Assert
        assert use_case.repository is mock_group_repository


class TestGetGroupByIdUseCase:
    async def test_get_by_id_found(
        self, mock_group_repository, sample_group_entity
    ):
        # Arrange
        mock_group_repository.get_by_id.return_value = sample_group_entity
        use_case = GetGroupByIdUseCase(mock_group_repository)

        # Act
        result = await use_case.execute(sample_group_entity.id)

        # Assert
        assert result is not None
        assert result.id == sample_group_entity.id
        mock_group_repository.get_by_id.assert_called_once_with(sample_group_entity.id)

    async def test_get_by_id_not_found_returns_none(self, mock_group_repository):
        # Arrange
        mock_group_repository.get_by_id.return_value = None
        use_case = GetGroupByIdUseCase(mock_group_repository)

        # Act
        result = await use_case.execute("nonexistent-id")

        # Assert
        assert result is None

    async def test_get_by_id_propagates_exception(self, mock_group_repository):
        # Arrange
        mock_group_repository.get_by_id.side_effect = RuntimeError("DB error")
        use_case = GetGroupByIdUseCase(mock_group_repository)

        # Act / Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await use_case.execute("some-id")
