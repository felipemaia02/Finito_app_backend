"""Tests for infrastructure/repositories/group_repository.py"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
from bson import ObjectId
from app.infrastructure.repositories.group_repository import MongoGroupRepository
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.entities.group_entity import Group


class AsyncIter:
    """Helper to create async iterables for mocking MongoDB cursors."""

    def __init__(self, items):
        self.items = list(items)
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


def make_group_doc(group_id=None):
    oid = ObjectId(group_id) if group_id else ObjectId()
    return {
        "_id": oid,
        "group_name": "Viagem Europa 2026",
        "user_ids": ["uid1", "uid2"],
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


def make_group_entity():
    return Group(
        id=str(ObjectId()),
        group_name="Viagem Europa 2026",
        user_ids=["uid1", "uid2"],
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


class TestMongoGroupRepositoryInit:
    def test_repository_is_instance_of_interface(self):
        # Arrange / Act
        repo = MongoGroupRepository()

        # Assert
        assert isinstance(repo, IGroupRepository)

    def test_repository_has_collection_name(self):
        # Arrange / Act
        repo = MongoGroupRepository()

        # Assert
        assert repo.collection_name == "groups"


class TestMongoGroupRepositoryDocumentConversion:
    def test_entity_to_document_without_id(self):
        # Arrange
        repo = MongoGroupRepository()
        entity = Group(group_name="Test")

        # Act
        doc = repo._entity_to_document(entity)

        # Assert
        assert "_id" in doc
        assert "group_name" in doc
        assert doc["group_name"] == "Test"

    def test_entity_to_document_with_existing_id(self):
        # Arrange
        repo = MongoGroupRepository()
        existing_id = str(ObjectId())
        entity = Group(id=existing_id, group_name="Test")

        # Act
        doc = repo._entity_to_document(entity)

        # Assert
        assert doc["_id"] == ObjectId(existing_id)

    def test_document_to_entity_converts_id(self):
        # Arrange
        repo = MongoGroupRepository()
        doc = make_group_doc()
        original_id = str(doc["_id"])  # save before _document_to_entity pops "_id"

        # Act
        entity = repo._document_to_entity(doc)

        # Assert
        assert entity is not None
        assert isinstance(entity, Group)
        assert entity.id == original_id
        assert entity.group_name == "Viagem Europa 2026"

    def test_document_to_entity_none_returns_none(self):
        # Arrange
        repo = MongoGroupRepository()

        # Act
        result = repo._document_to_entity(None)

        # Assert
        assert result is None


class TestMongoGroupRepositoryCreate:
    async def test_create_success(self):
        # Arrange
        repo = MongoGroupRepository()
        entity = make_group_entity()
        inserted_id = ObjectId()
        mock_col = MagicMock()
        mock_col.insert_one = AsyncMock(return_value=MagicMock(inserted_id=inserted_id))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.create(entity)

        # Assert
        assert result.id == str(inserted_id)
        mock_col.insert_one.assert_called_once()

    async def test_create_propagates_exception(self):
        # Arrange
        repo = MongoGroupRepository()
        entity = make_group_entity()
        mock_col = MagicMock()
        mock_col.insert_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError, match="DB error"):
                await repo.create(entity)


class TestMongoGroupRepositoryGetById:
    async def test_get_by_id_found(self):
        # Arrange
        repo = MongoGroupRepository()
        doc = make_group_doc()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(return_value=doc)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_by_id(str(doc["_id"]))

        # Assert
        assert result is not None
        assert isinstance(result, Group)

    async def test_get_by_id_not_found_returns_none(self):
        # Arrange
        repo = MongoGroupRepository()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(return_value=None)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_by_id(str(ObjectId()))

        # Assert
        assert result is None

    async def test_get_by_id_propagates_exception(self):
        # Arrange
        repo = MongoGroupRepository()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.get_by_id(str(ObjectId()))


class TestMongoGroupRepositoryGetAll:
    async def test_get_all_returns_list(self):
        # Arrange
        repo = MongoGroupRepository()
        docs = [make_group_doc(), make_group_doc()]

        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = AsyncIter(docs)  # sort returns async iterable

        mock_col = MagicMock()
        mock_col.find.return_value = mock_cursor

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_all()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2

    async def test_get_all_empty_returns_empty_list(self):
        # Arrange
        repo = MongoGroupRepository()

        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = AsyncIter([])

        mock_col = MagicMock()
        mock_col.find.return_value = mock_cursor

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_all()

        # Assert
        assert result == []

    async def test_get_all_propagates_exception(self):
        # Arrange
        repo = MongoGroupRepository()
        mock_col = MagicMock()
        mock_col.find.side_effect = RuntimeError("DB error")

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.get_all()


class TestMongoGroupRepositoryUpdate:
    async def test_update_success(self):
        # Arrange
        repo = MongoGroupRepository()
        entity = make_group_entity()
        doc = make_group_doc(entity.id)
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(return_value=MagicMock(matched_count=1))
        mock_col.find_one = AsyncMock(return_value=doc)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.update(entity.id, entity)

        # Assert
        assert result is not None
        mock_col.update_one.assert_called_once()

    async def test_update_not_found_returns_none(self):
        # Arrange
        repo = MongoGroupRepository()
        entity = make_group_entity()
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(return_value=MagicMock(matched_count=0))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.update(entity.id, entity)

        # Assert
        assert result is None

    async def test_update_propagates_exception(self):
        # Arrange
        repo = MongoGroupRepository()
        entity = make_group_entity()
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.update(entity.id, entity)


class TestMongoGroupRepositoryDelete:
    async def test_delete_success_returns_true(self):
        # Arrange
        repo = MongoGroupRepository()
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(return_value=MagicMock(matched_count=1))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.delete(str(ObjectId()))

        # Assert
        assert result is True

    async def test_delete_not_found_returns_false(self):
        # Arrange
        repo = MongoGroupRepository()
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(return_value=MagicMock(matched_count=0))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.delete(str(ObjectId()))

        # Assert
        assert result is False

    async def test_delete_propagates_exception(self):
        # Arrange
        repo = MongoGroupRepository()
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.delete(str(ObjectId()))


class TestMongoGroupRepositoryExists:
    async def test_exists_true(self):
        # Arrange
        repo = MongoGroupRepository()
        mock_col = MagicMock()
        mock_col.count_documents = AsyncMock(return_value=1)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.exists(str(ObjectId()))

        # Assert
        assert result is True

    async def test_exists_false(self):
        # Arrange
        repo = MongoGroupRepository()
        mock_col = MagicMock()
        mock_col.count_documents = AsyncMock(return_value=0)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.exists(str(ObjectId()))

        # Assert
        assert result is False

    async def test_exists_propagates_exception(self):
        # Arrange
        repo = MongoGroupRepository()
        mock_col = MagicMock()
        mock_col.count_documents = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.exists(str(ObjectId()))
