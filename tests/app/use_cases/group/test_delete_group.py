"""Tests for use_cases/group/delete_group.py"""

import pytest
from app.use_cases.group.delete_group import DeleteGroupUseCase


class TestDeleteGroupUseCaseInit:
    def test_init_stores_repository(self, mock_group_repository):
        # Arrange / Act
        use_case = DeleteGroupUseCase(mock_group_repository)

        # Assert
        assert use_case.repository is mock_group_repository


class TestDeleteGroupUseCase:
    async def test_delete_success_returns_true(self, mock_group_repository):
        # Arrange
        mock_group_repository.delete.return_value = True
        use_case = DeleteGroupUseCase(mock_group_repository)

        # Act
        result = await use_case.execute("group-id")

        # Assert
        assert result is True
        mock_group_repository.delete.assert_called_once_with("group-id")

    async def test_delete_not_found_returns_false(self, mock_group_repository):
        # Arrange
        mock_group_repository.delete.return_value = False
        use_case = DeleteGroupUseCase(mock_group_repository)

        # Act
        result = await use_case.execute("nonexistent-id")

        # Assert
        assert result is False

    async def test_delete_propagates_exception(self, mock_group_repository):
        # Arrange
        mock_group_repository.delete.side_effect = RuntimeError("DB error")
        use_case = DeleteGroupUseCase(mock_group_repository)

        # Act / Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await use_case.execute("group-id")
