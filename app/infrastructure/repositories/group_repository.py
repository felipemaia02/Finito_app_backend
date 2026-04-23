"""MongoDB implementation of the Group repository."""

from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.entities.group_entity import Group
from app.infrastructure.database.database import Database
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class MongoGroupRepository(IGroupRepository):
    """MongoDB implementation of the group repository."""

    def __init__(self):
        self.collection_name = "groups"

    def _get_collection(self):
        return Database.get_db()[self.collection_name]

    def _entity_to_document(self, entity: Group) -> dict:
        doc = entity.model_dump(exclude={"id"})
        doc["_id"] = ObjectId(entity.id) if entity.id else ObjectId()
        return doc

    def _document_to_entity(self, doc: dict) -> Group:
        if doc:
            doc["id"] = str(doc.pop("_id"))
            return Group(**doc)
        return None

    async def create(self, entity: Group) -> Group:
        try:
            collection = self._get_collection()
            doc = entity.model_dump(exclude={"id"})
            result = await collection.insert_one(doc)
            entity.id = str(result.inserted_id)
            logger.info(f"Created group with ID: {entity.id}")
            return entity
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            raise

    async def get_by_id(self, id: str) -> Optional[Group]:
        try:
            collection = self._get_collection()
            doc = await collection.find_one({"_id": ObjectId(id), "is_deleted": False})
            if doc:
                logger.info(f"Retrieved group with ID: {id}")
                return self._document_to_entity(doc)
            logger.warning(f"Group not found with ID: {id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving group by ID {id}: {e}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Group]:
        try:
            collection = self._get_collection()
            cursor = (
                collection.find({"is_deleted": False})
                .skip(skip)
                .limit(limit)
                .sort("created_at", -1)
            )
            groups = []
            async for doc in cursor:
                groups.append(self._document_to_entity(doc))
            logger.info(f"Retrieved {len(groups)} groups")
            return groups
        except Exception as e:
            logger.error(f"Error retrieving groups: {e}")
            raise

    async def update(self, id: str, entity: Group) -> Optional[Group]:
        try:
            collection = self._get_collection()
            update_data = entity.model_dump(exclude={"id", "created_at"})
            result = await collection.update_one(
                {"_id": ObjectId(id)}, {"$set": update_data}
            )
            if result.matched_count > 0:
                logger.info(f"Updated group with ID: {id}")
                return await self.get_by_id(id)
            logger.warning(f"Group not found for update with ID: {id}")
            return None
        except Exception as e:
            logger.error(f"Error updating group {id}: {e}")
            raise

    async def delete(self, id: str) -> bool:
        try:
            collection = self._get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(id), "is_deleted": False},
                {
                    "$set": {
                        "is_deleted": True,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )
            if result.matched_count > 0:
                logger.info(f"Soft deleted group with ID: {id}")
                return True
            logger.warning(f"Group not found for deletion with ID: {id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting group {id}: {e}")
            raise

    async def exists(self, id: str) -> bool:
        try:
            collection = self._get_collection()
            count = await collection.count_documents(
                {"_id": ObjectId(id), "is_deleted": False}, limit=1
            )
            return count > 0
        except Exception as e:
            logger.error(f"Error checking group existence {id}: {e}")
            raise

    async def get_by_user_id(self, user_id: str) -> List[Group]:
        try:
            collection = self._get_collection()
            cursor = collection.find(
                {"user_ids": user_id, "is_deleted": False}
            ).sort("created_at", -1)
            groups = []
            async for doc in cursor:
                groups.append(self._document_to_entity(doc))
            logger.info(f"Retrieved {len(groups)} groups for user {user_id}")
            return groups
        except Exception as e:
            logger.error(f"Error retrieving groups for user {user_id}: {e}")
            raise
