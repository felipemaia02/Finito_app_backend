"""
MongoDB implementation of the Expense repository.
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.entities.expense_entity import Expense
from app.infrastructure.database import Database
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

class MongoExpenseRepository(IExpenseRepository):
    """
    MongoDB implementation of the expense repository.
    Handles persistence and retrieval of expense entities.
    """

    def __init__(self):
        """Initialize repository with MongoDB collection."""
        self.collection_name = "expenses"

    def _get_collection(self):
        """Get the MongoDB collection for expenses."""
        db = Database.get_db()
        return db[self.collection_name]
    
    def _entity_to_document(self, entity: Expense) -> dict:
        """
        Convert entity to MongoDB document.
        
        Args:
            entity: Expense entity to convert
            
        Returns:
            Dictionary suitable for MongoDB insertion
        """
        doc = entity.model_dump(exclude={"id"})
        doc["_id"] = ObjectId(entity.id) if entity.id else ObjectId()
        return doc
    
    def _document_to_entity(self, doc: dict) -> Expense:
        """
        Convert MongoDB document to entity.
        
        Args:
            doc: MongoDB document
            
        Returns:
            Expense entity
        """
        if doc:
            doc["id"] = str(doc.pop("_id"))
            return Expense(**doc)
        return None
    
    async def create(self, entity: Expense) -> Expense:
        """
        Create a new expense in the database.
        
        Args:
            entity: Expense entity to create
            
        Returns:
            Created expense with generated ID
        """
        try:
            collection = self._get_collection()
            doc = entity.model_dump(exclude={"id"})
            
            result = await collection.insert_one(doc)
            entity.id = str(result.inserted_id)
            
            logger.info(f"Created expense with ID: {entity.id} for group: {entity.group_id}")
            return entity
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            raise
    
    async def get_by_id(self, id: str) -> Optional[Expense]:
        """
        Get an expense by its ID (excludes soft-deleted expenses).
        
        Args:
            id: Expense ID
            
        Returns:
            Expense entity if found and not deleted, None otherwise
        """
        try:
            collection = self._get_collection()
            doc = await collection.find_one({"_id": ObjectId(id), "is_deleted": False})
            
            if doc:
                logger.info(f"Retrieved expense with ID: {id}")
                return self._document_to_entity(doc)
            
            logger.warning(f"Expense not found with ID: {id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving expense by ID {id}: {e}")
            raise
    
    async def get_all(self, group_id: str, skip: int = 0, limit: int = 100) -> List[Expense]:
        """
        Get all active expenses for a group (from all participants).
        Retrieves expenses added by any participant to this group.
        
        Args:
            group_id: ID of the expense group
            skip: Number of expenses to skip
            limit: Maximum number of expenses to return
            
        Returns:
            List of active expense entities from all participants in the group
        """
        try:
            collection = self._get_collection()
            # Query only by group_id and is_deleted, regardless of who spent
            cursor = collection.find({"group_id": group_id, "is_deleted": False}).skip(skip).limit(limit).sort("date", -1)
            
            expenses = []
            async for doc in cursor:
                expenses.append(self._document_to_entity(doc))
            
            logger.info(f"Retrieved {len(expenses)} active expenses for group: {group_id}")
            return expenses
        except Exception as e:
            logger.error(f"Error retrieving expenses for group {group_id}: {e}")
            raise
    
    async def update(self, id: str, entity: Expense) -> Optional[Expense]:
        """
        Update an existing expense.
        
        Args:
            id: Expense ID to update
            entity: Updated expense data
            
        Returns:
            Updated expense if found, None otherwise
        """
        try:
            collection = self._get_collection()
            update_data = entity.model_dump(exclude={"id", "created_at"})
            update_data["updated_at"] = entity.updated_at
            
            result = await collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                logger.info(f"Updated expense with ID: {id}")
                return await self.get_by_id(id)
            
            logger.warning(f"Expense not found for update with ID: {id}")
            return None
        except Exception as e:
            logger.error(f"Error updating expense {id}: {e}")
            raise

    async def delete(self, id: str) -> bool:
        """
        Soft delete an expense by marking it as deleted.
        The expense is not removed from the database, only hidden from queries.
        
        Args:
            id: Expense ID to delete
            
        Returns:
            True if soft deleted, False if not found
        """
        try:
            collection = self._get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(id), "is_deleted": False},
                {"$set": {"is_deleted": True, "updated_at": datetime.now(timezone.utc)}}
            )
            
            if result.matched_count > 0:
                logger.info(f"Soft deleted expense with ID: {id}")
                return True
            
            logger.warning(f"Expense not found for deletion with ID: {id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting expense {id}: {e}")
            raise

    async def exists(self, id: str) -> bool:
        """
        Check if an active (non-deleted) expense exists.
        
        Args:
            id: Expense ID to check
            
        Returns:
            True if exists and not deleted, False otherwise
        """
        try:
            collection = self._get_collection()
            count = await collection.count_documents({"_id": ObjectId(id), "is_deleted": False}, limit=1)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking expense existence {id}: {e}")
            raise

    async def get_amounts_and_types(self, group_id: str) -> List[Dict[str, any]]:
        """
        Get only amount_cents and type_expense for all active expenses in a group.
        Optimized query that retrieves data from all participants (excludes soft-deleted).
        
        Args:
            group_id: ID of the expense group
            
        Returns:
            List of dictionaries with amount_cents and type_expense from all participants
        """
        try:
            collection = self._get_collection()
            cursor = collection.find(
                {"group_id": group_id, "is_deleted": False},
                {"amount_cents": 1, "type_expense": 1, "_id": 0}
            )
            
            results = []
            async for doc in cursor:
                results.append({
                    "amount_cents": doc.get("amount_cents"),
                    "type_expense": doc.get("type_expense")
                })
            
            logger.info(f"Retrieved amounts and types for {len(results)} active expenses in group: {group_id}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving amounts and types for group {group_id}: {e}")
            raise
    
    async def restore(self, id: str) -> bool:
        """
        Restore a soft-deleted expense by marking is_deleted as False.
        
        Args:
            id: Expense ID to restore
            
        Returns:
            True if restored, False if not found or already active
        """
        try:
            collection = self._get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(id), "is_deleted": True},
                {"$set": {"is_deleted": False, "updated_at": datetime.now(timezone.utc)}}
            )
            
            if result.matched_count > 0:
                logger.info(f"Restored soft-deleted expense with ID: {id}")
                return True
            
            logger.warning(f"Expense not found for restoration with ID: {id} (might not be deleted)")
            return False
        except Exception as e:
            logger.error(f"Error restoring expense {id}: {e}")
            raise
    
    async def delete_permanently(self, id: str) -> bool:
        """
        Permanently delete an expense from database.
        Use with caution - this action cannot be undone.
        
        Args:
            id: Expense ID to permanently delete
            
        Returns:
            True if permanently deleted, False if not found
        """
        try:
            collection = self._get_collection()
            result = await collection.delete_one({"_id": ObjectId(id)})
            
            if result.deleted_count > 0:
                logger.warning(f"Permanently deleted expense with ID: {id} (IRREVERSIBLE)")
                return True
            
            logger.warning(f"Expense not found for permanent deletion with ID: {id}")
            return False
        except Exception as e:
            logger.error(f"Error permanently deleting expense {id}: {e}")
            raise
