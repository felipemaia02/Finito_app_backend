"""Tests for infrastructure/repositories/expense_repository.py"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
from bson import ObjectId
from app.infrastructure.repositories.expense_repository import MongoExpenseRepository
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.entities.expense_entity import Expense
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType


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


def make_expense_doc(expense_id=None):
    """Create a sample expense document."""
    oid = ObjectId(expense_id) if expense_id else ObjectId()
    return {
        "_id": oid,
        "group_id": "507f1f77bcf86cd799439012",
        "amount_cents": 5000,
        "category": ExpenseCategory.ENTERTAINMENT,
        "type_expense": ExpenseType.CREDIT_CARD,
        "description": "Movie tickets",
        "spent_by": "John Doe",
        "date": datetime.now(timezone.utc),
        "note": "Weekend movie",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_deleted": False,
    }


def make_expense_entity():
    """Create a sample expense entity."""
    return Expense(
        group_id="507f1f77bcf86cd799439012",
        amount_cents=5000,
        category=ExpenseCategory.ENTERTAINMENT,
        type_expense=ExpenseType.CREDIT_CARD,
        description="Movie tickets",
        spent_by="John Doe",
        date=datetime.now(timezone.utc),
        note="Weekend movie",
    )


class TestMongoExpenseRepositoryInitialization:
    """Test MongoExpenseRepository initialization"""

    def test_repository_can_be_instantiated(self):
        repo = MongoExpenseRepository()
        assert repo is not None

    def test_repository_implements_interface(self):
        repo = MongoExpenseRepository()
        assert isinstance(repo, IExpenseRepository)

    def test_collection_name_is_expenses(self):
        repo = MongoExpenseRepository()
        assert repo.collection_name == "expenses"


class TestMongoExpenseRepositoryMethods:
    """Test MongoExpenseRepository has required methods"""

    def test_repository_has_create(self):
        repo = MongoExpenseRepository()
        assert hasattr(repo, "create")

    def test_repository_has_get_all(self):
        repo = MongoExpenseRepository()
        assert hasattr(repo, "get_all")

    def test_repository_has_get_by_id(self):
        repo = MongoExpenseRepository()
        assert hasattr(repo, "get_by_id")

    def test_repository_has_update(self):
        repo = MongoExpenseRepository()
        assert hasattr(repo, "update")

    def test_repository_has_delete(self):
        repo = MongoExpenseRepository()
        assert hasattr(repo, "delete")

    def test_repository_has_get_amounts_and_types(self):
        repo = MongoExpenseRepository()
        assert hasattr(repo, "get_amounts_and_types")


class TestMongoExpenseRepositoryCallable:
    """Test MongoExpenseRepository methods are callable"""

    def test_create_is_callable(self):
        repo = MongoExpenseRepository()
        assert callable(repo.create)

    def test_get_all_is_callable(self):
        repo = MongoExpenseRepository()
        assert callable(repo.get_all)

    def test_get_by_id_is_callable(self):
        repo = MongoExpenseRepository()
        assert callable(repo.get_by_id)

    def test_update_is_callable(self):
        repo = MongoExpenseRepository()
        assert callable(repo.update)

    def test_delete_is_callable(self):
        repo = MongoExpenseRepository()
        assert callable(repo.delete)


class TestMongoExpenseRepositoryHelpers:
    """Test internal helper methods."""

    def test_document_to_entity_with_valid_doc(self):
        repo = MongoExpenseRepository()
        doc = make_expense_doc()
        entity = repo._document_to_entity(doc)
        assert entity is not None
        assert isinstance(entity, Expense)

    def test_document_to_entity_with_none(self):
        repo = MongoExpenseRepository()
        result = repo._document_to_entity(None)
        assert result is None

    def test_entity_to_document(self):
        repo = MongoExpenseRepository()
        entity = make_expense_entity()
        doc = repo._entity_to_document(entity)
        assert "_id" in doc
        assert "id" not in doc

    def test_entity_to_document_with_id(self):
        repo = MongoExpenseRepository()
        entity = make_expense_entity()
        entity.id = str(ObjectId())
        doc = repo._entity_to_document(entity)
        assert "_id" in doc
        assert isinstance(doc["_id"], ObjectId)


class TestMongoExpenseRepositoryCreate:
    """Test create method."""

    @pytest.mark.asyncio
    async def test_create_success(self):
        repo = MongoExpenseRepository()
        entity = make_expense_entity()
        inserted_id = ObjectId()

        mock_collection = AsyncMock()
        insert_result = MagicMock()
        insert_result.inserted_id = inserted_id
        mock_collection.insert_one = AsyncMock(return_value=insert_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.create(entity)

        assert result is not None
        assert result.id == str(inserted_id)

    @pytest.mark.asyncio
    async def test_create_raises_on_exception(self):
        repo = MongoExpenseRepository()
        entity = make_expense_entity()

        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception, match="DB error"):
                await repo.create(entity)


class TestMongoExpenseRepositoryGetById:
    """Test get_by_id method."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())
        doc = make_expense_doc(expense_id)

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=doc)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_by_id(expense_id)

        assert result is not None
        assert result.id == expense_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_by_id(expense_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_raises_on_exception(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.get_by_id(expense_id)


class TestMongoExpenseRepositoryGetAll:
    """Test get_all method."""

    @pytest.mark.asyncio
    async def test_get_all_returns_expenses(self):
        repo = MongoExpenseRepository()
        group_id = "507f1f77bcf86cd799439012"
        docs = [make_expense_doc(), make_expense_doc()]

        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = AsyncIter(docs)

        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_all(group_id)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_empty(self):
        repo = MongoExpenseRepository()
        group_id = "507f1f77bcf86cd799439012"

        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = AsyncIter([])

        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_all(group_id)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_raises_on_exception(self):
        repo = MongoExpenseRepository()
        group_id = "507f1f77bcf86cd799439012"

        mock_collection = MagicMock()
        mock_collection.find.side_effect = Exception("DB error")

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.get_all(group_id)


class TestMongoExpenseRepositoryUpdate:
    """Test update method."""

    @pytest.mark.asyncio
    async def test_update_success(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())
        entity = make_expense_entity()
        entity.id = expense_id
        doc = make_expense_doc(expense_id)

        update_result = MagicMock()
        update_result.matched_count = 1

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)
        mock_collection.find_one = AsyncMock(return_value=doc)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.update(expense_id, entity)

        assert result is not None

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())
        entity = make_expense_entity()

        update_result = MagicMock()
        update_result.matched_count = 0

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.update(expense_id, entity)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_raises_on_exception(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())
        entity = make_expense_entity()

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.update(expense_id, entity)


class TestMongoExpenseRepositoryDelete:
    """Test delete (soft delete) method."""

    @pytest.mark.asyncio
    async def test_delete_success(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        update_result = MagicMock()
        update_result.matched_count = 1

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.delete(expense_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        update_result = MagicMock()
        update_result.matched_count = 0

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.delete(expense_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_raises_on_exception(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.delete(expense_id)


class TestMongoExpenseRepositoryExists:
    """Test exists method."""

    @pytest.mark.asyncio
    async def test_exists_true(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.count_documents = AsyncMock(return_value=1)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.exists(expense_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.count_documents = AsyncMock(return_value=0)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.exists(expense_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_raises_on_exception(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.count_documents = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.exists(expense_id)


class TestMongoExpenseRepositoryGetAmountsAndTypes:
    """Test get_amounts_and_types method."""

    @pytest.mark.asyncio
    async def test_get_amounts_and_types_success(self):
        repo = MongoExpenseRepository()
        group_id = "507f1f77bcf86cd799439012"
        docs = [
            {"amount_cents": 1000, "type_expense": ExpenseType.CASH},
            {"amount_cents": 2000, "type_expense": ExpenseType.CREDIT_CARD},
        ]

        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda self: AsyncIter(docs).__aiter__()

        mock_collection = MagicMock()
        mock_collection.find.return_value = AsyncIter(docs)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_amounts_and_types(group_id)

        assert len(result) == 2
        assert result[0]["amount_cents"] == 1000

    @pytest.mark.asyncio
    async def test_get_amounts_and_types_empty(self):
        repo = MongoExpenseRepository()
        group_id = "507f1f77bcf86cd799439012"

        mock_collection = MagicMock()
        mock_collection.find.return_value = AsyncIter([])

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_amounts_and_types(group_id)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_amounts_and_types_raises_on_exception(self):
        repo = MongoExpenseRepository()
        group_id = "507f1f77bcf86cd799439012"

        mock_collection = MagicMock()
        mock_collection.find.side_effect = Exception("DB error")

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.get_amounts_and_types(group_id)


class TestMongoExpenseRepositoryRestore:
    """Test restore method."""

    @pytest.mark.asyncio
    async def test_restore_success(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        update_result = MagicMock()
        update_result.matched_count = 1

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.restore(expense_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_restore_not_found(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        update_result = MagicMock()
        update_result.matched_count = 0

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.restore(expense_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_restore_raises_on_exception(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.restore(expense_id)


class TestMongoExpenseRepositoryDeletePermanently:
    """Test delete_permanently method."""

    @pytest.mark.asyncio
    async def test_delete_permanently_success(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        delete_result = MagicMock()
        delete_result.deleted_count = 1

        mock_collection = AsyncMock()
        mock_collection.delete_one = AsyncMock(return_value=delete_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.delete_permanently(expense_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_permanently_not_found(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        delete_result = MagicMock()
        delete_result.deleted_count = 0

        mock_collection = AsyncMock()
        mock_collection.delete_one = AsyncMock(return_value=delete_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.delete_permanently(expense_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_permanently_raises_on_exception(self):
        repo = MongoExpenseRepository()
        expense_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.delete_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.expense_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.delete_permanently(expense_id)
