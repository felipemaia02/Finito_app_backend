"""
MongoDB implementation of the email verification token repository.
"""

from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from app.domain.interfaces.email_verification_repository_interface import (
    IEmailVerificationRepository,
)
from app.domain.entities.email_verification_token_entity import EmailVerificationToken
from app.infrastructure.database.database import Database
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class MongoEmailVerificationRepository(IEmailVerificationRepository):
    """MongoDB implementation of IEmailVerificationRepository."""

    def __init__(self):
        self.collection_name = "email_verification_tokens"

    def _get_collection(self):
        return Database.get_db()[self.collection_name]

    def _entity_to_document(self, entity: EmailVerificationToken) -> dict:
        doc = entity.model_dump(exclude={"id"})
        doc["_id"] = ObjectId(entity.id) if entity.id else ObjectId()
        return doc

    def _document_to_entity(self, doc: dict) -> Optional[EmailVerificationToken]:
        if doc:
            doc["id"] = str(doc.pop("_id"))
            return EmailVerificationToken(**doc)
        return None

    # ------------------------------------------------------------------ CRUD

    async def create(self, entity: EmailVerificationToken) -> EmailVerificationToken:
        try:
            collection = self._get_collection()
            doc = self._entity_to_document(entity)
            result = await collection.insert_one(doc)
            entity.id = str(result.inserted_id)
            logger.info(f"Created email verification token with ID: {entity.id}")
            return entity
        except Exception as e:
            logger.error(f"Error creating email verification token: {e}")
            raise

    async def get_by_id(self, id: str) -> Optional[EmailVerificationToken]:
        try:
            collection = self._get_collection()
            doc = await collection.find_one({"_id": ObjectId(id)})
            return self._document_to_entity(doc) if doc else None
        except Exception as e:
            logger.error(f"Error fetching email verification token by id: {e}")
            raise

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> List[EmailVerificationToken]:
        try:
            collection = self._get_collection()
            cursor = collection.find({}).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [self._document_to_entity(d) for d in docs if d]
        except Exception as e:
            logger.error(f"Error fetching email verification tokens: {e}")
            raise

    async def update(
        self, id: str, entity: EmailVerificationToken
    ) -> Optional[EmailVerificationToken]:
        try:
            collection = self._get_collection()
            doc = self._entity_to_document(entity)
            result = await collection.replace_one({"_id": ObjectId(id)}, doc)
            return entity if result.matched_count > 0 else None
        except Exception as e:
            logger.error(f"Error updating email verification token: {e}")
            raise

    async def exists(self, id: str) -> bool:
        try:
            collection = self._get_collection()
            count = await collection.count_documents({"_id": ObjectId(id)})
            return count > 0
        except Exception as e:
            logger.error(f"Error checking email verification token existence: {e}")
            raise

    async def delete(self, id: str) -> bool:
        try:
            collection = self._get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(id)}, {"$set": {"is_used": True}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting email verification token: {e}")
            raise

    # -------------------------------------------------------- Custom methods

    async def get_valid_token_by_user_id(
        self, user_id: str
    ) -> Optional[EmailVerificationToken]:
        """Return the active (not used) token for a user."""
        try:
            collection = self._get_collection()
            doc = await collection.find_one(
                {"user_id": user_id, "is_used": False},
                sort=[("created_at", -1)],
            )
            return self._document_to_entity(doc) if doc else None
        except Exception as e:
            logger.error(f"Error fetching valid verification token: {e}")
            raise

    async def get_latest_by_user_id(
        self, user_id: str
    ) -> Optional[EmailVerificationToken]:
        """Return the most recent token for a user regardless of status."""
        try:
            collection = self._get_collection()
            doc = await collection.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)],
            )
            return self._document_to_entity(doc) if doc else None
        except Exception as e:
            logger.error(f"Error fetching latest verification token: {e}")
            raise

    async def mark_as_used(self, token_id: str) -> None:
        try:
            collection = self._get_collection()
            now = datetime.now(timezone.utc)
            await collection.update_one(
                {"_id": ObjectId(token_id)},
                {"$set": {"is_used": True, "updated_at": now}},
            )
            logger.info(f"Marked verification token {token_id} as used")
        except Exception as e:
            logger.error(f"Error marking token as used: {e}")
            raise

    async def increment_attempts(self, token_id: str) -> None:
        try:
            collection = self._get_collection()
            now = datetime.now(timezone.utc)
            await collection.update_one(
                {"_id": ObjectId(token_id)},
                {"$inc": {"attempts": 1}, "$set": {"updated_at": now}},
            )
        except Exception as e:
            logger.error(f"Error incrementing token attempts: {e}")
            raise

    async def invalidate_all_by_user_id(self, user_id: str) -> None:
        try:
            collection = self._get_collection()
            now = datetime.now(timezone.utc)
            await collection.update_many(
                {"user_id": user_id, "is_used": False},
                {"$set": {"is_used": True, "updated_at": now}},
            )
            logger.info(f"Invalidated all active tokens for user_id={user_id}")
        except Exception as e:
            logger.error(f"Error invalidating tokens: {e}")
            raise
