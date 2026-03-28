"""Tests for infrastructure/repositories/user_repository.py"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime, timezone
from bson import ObjectId
from app.infrastructure.repositories.user_repository import MongoUserRepository
from app.domain.entities.user_entity import User


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


def make_user_doc(user_id=None):
    """Create a sample user document."""
    oid = ObjectId(user_id) if user_id else ObjectId()
    return {
        "_id": oid,
        "name": "John Silva",
        "email": "john@example.com",
        "password": "$2b$12$abcdefghijklmnopqrstuvwxyz1234567890",
        "date_birth": datetime(1990, 5, 15),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


def make_user_entity():
    """Create a sample user entity."""
    return User(
        name="John Silva",
        email="john@example.com",
        password="$2b$12$abcdefghijklmnopqrstuvwxyz1234567890",
        date_birth=date(1990, 5, 15),
    )


class TestMongoUserRepository:
    """Test cases for MongoUserRepository."""

    def test_repository_initialization(self):
        repo = MongoUserRepository()
        assert repo.collection_name == "users"

    def test_repository_can_be_instantiated(self):
        repo = MongoUserRepository()
        assert repo is not None


class TestMongoUserRepositoryHelpers:
    """Test internal helper methods."""

    def test_document_to_entity_with_valid_doc(self):
        repo = MongoUserRepository()
        doc = make_user_doc()
        entity = repo._document_to_entity(doc)
        assert entity is not None
        assert isinstance(entity, User)
        assert entity.email == "john@example.com"

    def test_document_to_entity_converts_datetime_to_date(self):
        repo = MongoUserRepository()
        doc = make_user_doc()
        doc["date_birth"] = datetime(1990, 5, 15)
        entity = repo._document_to_entity(doc)
        assert isinstance(entity.date_birth, date)

    def test_document_to_entity_with_none(self):
        repo = MongoUserRepository()
        result = repo._document_to_entity(None)
        assert result is None

    def test_entity_to_document_with_date_birth(self):
        repo = MongoUserRepository()
        entity = make_user_entity()
        doc = repo._entity_to_document(entity)
        assert "_id" in doc
        assert "id" not in doc

    def test_entity_to_document_with_id(self):
        repo = MongoUserRepository()
        entity = make_user_entity()
        entity.id = str(ObjectId())
        doc = repo._entity_to_document(entity)
        assert "_id" in doc
        assert isinstance(doc["_id"], ObjectId)

    def test_entity_to_document_converts_date_to_datetime(self):
        repo = MongoUserRepository()
        entity = make_user_entity()
        doc = repo._entity_to_document(entity)
        assert isinstance(doc["date_birth"], datetime)


class TestMongoUserRepositoryCreate:
    """Test create method."""

    @pytest.mark.asyncio
    async def test_create_success(self):
        repo = MongoUserRepository()
        entity = make_user_entity()
        inserted_id = ObjectId()

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        insert_result = MagicMock()
        insert_result.inserted_id = inserted_id
        mock_collection.insert_one = AsyncMock(return_value=insert_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.create(entity)

        assert result is not None
        assert result.id == str(inserted_id)

    @pytest.mark.asyncio
    async def test_create_raises_on_duplicate_email(self):
        repo = MongoUserRepository()
        entity = make_user_entity()
        existing_doc = make_user_doc()

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=existing_doc)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(ValueError, match="already registered"):
                await repo.create(entity)

    @pytest.mark.asyncio
    async def test_create_raises_on_exception(self):
        repo = MongoUserRepository()
        entity = make_user_entity()

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception, match="DB error"):
                await repo.create(entity)


class TestMongoUserRepositoryGetById:
    """Test get_by_id method."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())
        doc = make_user_doc(user_id)

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=doc)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_by_id(user_id)

        assert result is not None
        assert result.id == user_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_by_id(user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_raises_on_exception(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.get_by_id(user_id)


class TestMongoUserRepositoryGetAll:
    """Test get_all method."""

    @pytest.mark.asyncio
    async def test_get_all_returns_users(self):
        repo = MongoUserRepository()
        docs = [make_user_doc(), make_user_doc()]

        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = AsyncIter(docs)

        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_all()

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_empty(self):
        repo = MongoUserRepository()

        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = AsyncIter([])

        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_all()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self):
        repo = MongoUserRepository()
        docs = [make_user_doc()]

        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = AsyncIter(docs)

        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_all(skip=10, limit=50)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_all_raises_on_exception(self):
        repo = MongoUserRepository()

        mock_collection = MagicMock()
        mock_collection.find.side_effect = Exception("DB error")

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.get_all()


class TestMongoUserRepositoryGetByEmail:
    """Test get_by_email method."""

    @pytest.mark.asyncio
    async def test_get_by_email_found(self):
        repo = MongoUserRepository()
        email = "john@example.com"
        doc = make_user_doc()
        doc["email"] = email

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=doc)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_by_email(email)

        assert result is not None
        assert result.email == email

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self):
        repo = MongoUserRepository()

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.get_by_email("nonexistent@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_raises_on_exception(self):
        repo = MongoUserRepository()

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.get_by_email("test@example.com")


class TestMongoUserRepositoryEmailExists:
    """Test email_exists method."""

    @pytest.mark.asyncio
    async def test_email_exists_true(self):
        repo = MongoUserRepository()
        email = "john@example.com"
        doc = make_user_doc()

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=doc)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.email_exists(email)

        assert result is True

    @pytest.mark.asyncio
    async def test_email_exists_false(self):
        repo = MongoUserRepository()

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.email_exists("nonexistent@example.com")

        assert result is False

    @pytest.mark.asyncio
    async def test_email_exists_raises_on_exception(self):
        repo = MongoUserRepository()

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.email_exists("test@example.com")


class TestMongoUserRepositoryUpdate:
    """Test update method."""

    @pytest.mark.asyncio
    async def test_update_success(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())
        entity = make_user_entity()
        entity.id = user_id
        doc = make_user_doc(user_id)

        update_result = MagicMock()
        update_result.matched_count = 1

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)
        mock_collection.find_one = AsyncMock(return_value=doc)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.update(user_id, entity)

        assert result is not None

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())
        entity = make_user_entity()

        update_result = MagicMock()
        update_result.matched_count = 0

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.update(user_id, entity)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_raises_on_exception(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())
        entity = make_user_entity()

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.update(user_id, entity)


class TestMongoUserRepositoryDelete:
    """Test delete (soft delete) method."""

    @pytest.mark.asyncio
    async def test_delete_success(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())

        update_result = MagicMock()
        update_result.matched_count = 1

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.delete(user_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())

        update_result = MagicMock()
        update_result.matched_count = 0

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(return_value=update_result)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.delete(user_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_raises_on_exception(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.update_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.delete(user_id)


class TestMongoUserRepositoryExists:
    """Test exists method."""

    @pytest.mark.asyncio
    async def test_exists_true(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())
        doc = make_user_doc(user_id)

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=doc)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.exists(user_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            result = await repo.exists(user_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_raises_on_exception(self):
        repo = MongoUserRepository()
        user_id = str(ObjectId())

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(side_effect=Exception("DB error"))

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch(
            "app.infrastructure.repositories.user_repository.Database.get_db",
            return_value=mock_db,
        ):
            with pytest.raises(Exception):
                await repo.exists(user_id)
