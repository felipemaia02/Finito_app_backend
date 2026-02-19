"""
MongoDB implementation of the User repository.
"""

from typing import List, Optional
from datetime import datetime, date, timezone
from bson import ObjectId
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.entities.user_entity import User
from app.infrastructure.database.database import Database
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class MongoUserRepository(IUserRepository):
    """
    MongoDB implementation of the user repository.
    Handles persistence and retrieval of user entities.
    """

    def __init__(self):
        """Initialize repository with MongoDB collection."""
        self.collection_name = "users"

    def _get_collection(self):
        """Get the MongoDB collection for users."""
        db = Database.get_db()
        return db[self.collection_name]
    
    def _entity_to_document(self, entity: User) -> dict:
        """
        Convert entity to MongoDB document.
        
        Args:
            entity: User entity to convert
            
        Returns:
            Dictionary suitable for MongoDB insertion
        """
        doc = entity.model_dump(exclude={"id"})
        doc["_id"] = ObjectId(entity.id) if entity.id else ObjectId()
        
        # Convert date to datetime for MongoDB compatibility
        if "data_nascimento" in doc and isinstance(doc["data_nascimento"], date):
            if not isinstance(doc["data_nascimento"], datetime):
                doc["data_nascimento"] = datetime.combine(doc["data_nascimento"], datetime.min.time())
        
        return doc
    
    def _document_to_entity(self, doc: dict) -> User:
        """
        Convert MongoDB document to entity.
        
        Args:
            doc: MongoDB document
            
        Returns:
            User entity
        """
        if doc:
            doc["id"] = str(doc.pop("_id"))
            
            # Convert datetime back to date if needed
            if "data_nascimento" in doc and isinstance(doc["data_nascimento"], datetime):
                doc["data_nascimento"] = doc["data_nascimento"].date()
            
            return User(**doc)
        return None
    
    async def create(self, entity: User) -> User:
        """
        Create a new user in the database.
        
        Args:
            entity: User entity to create
            
        Returns:
            Created user with generated ID
            
        Raises:
            ValueError: If email already exists
            Exception: If database operation fails
        """
        try:
            collection = self._get_collection()
            
            existing_user = await collection.find_one({"email": entity.email})
            if existing_user:
                logger.warning(f"User with email {entity.email} already exists")
                raise ValueError(f"Email {entity.email} is already registered")
            
            doc = self._entity_to_document(entity)
            result = await collection.insert_one(doc)
            entity.id = str(result.inserted_id)
            
            logger.info(f"Created user with ID: {entity.id} and email: {entity.email}")
            return entity
        except ValueError as ve:
            logger.warning(f"Validation error creating user: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_by_id(self, id: str) -> Optional[User]:
        """
        Get a user by their ID (only active users).
        
        Args:
            id: User ID
            
        Returns:
            User entity if found and active, None otherwise
        """
        try:
            collection = self._get_collection()
            doc = await collection.find_one({"_id": ObjectId(id), "is_active": True})
            
            if doc:
                logger.info(f"Retrieved user with ID: {id}")
                return self._document_to_entity(doc)
            
            logger.warning(f"User not found with ID: {id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by ID {id}: {e}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all active users with pagination.
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of active user entities
        """
        try:
            collection = self._get_collection()
            cursor = collection.find({"is_active": True}).skip(skip).limit(limit).sort("created_at", -1)
            
            users = []
            async for doc in cursor:
                users.append(self._document_to_entity(doc))
            
            logger.info(f"Retrieved {len(users)} active users")
            return users
        except Exception as e:
            logger.error(f"Error retrieving users: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email address.
        
        Args:
            email: User's email address
            
        Returns:
            User entity if found and active, None otherwise
        """
        try:
            collection = self._get_collection()
            doc = await collection.find_one({"email": email, "is_active": True})
            
            if doc:
                logger.info(f"Retrieved user with email: {email}")
                return self._document_to_entity(doc)
            
            logger.warning(f"User not found with email: {email}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {e}")
            raise
    
    async def email_exists(self, email: str) -> bool:
        """
        Check if an email already exists in the system.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email exists, False otherwise
        """
        try:
            collection = self._get_collection()
            doc = await collection.find_one({"email": email})
            return doc is not None
        except Exception as e:
            logger.error(f"Error checking email existence for {email}: {e}")
            raise
    
    async def update(self, id: str, entity: User) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            id: User ID to update
            entity: Updated user data
            
        Returns:
            Updated user if found, None otherwise
        """
        try:
            collection = self._get_collection()
            update_data = entity.model_dump(exclude={"id", "created_at"})
            update_data["updated_at"] = entity.updated_at
            
            # Convert date to datetime for MongoDB compatibility
            if "data_nascimento" in update_data and isinstance(update_data["data_nascimento"], date):
                if not isinstance(update_data["data_nascimento"], datetime):
                    update_data["data_nascimento"] = datetime.combine(update_data["data_nascimento"], datetime.min.time())
            
            result = await collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                logger.info(f"Updated user with ID: {id}")
                return await self.get_by_id(id)
            
            logger.warning(f"User not found for update with ID: {id}")
            return None
        except Exception as e:
            logger.error(f"Error updating user with ID {id}: {e}")
            raise
    
    async def delete(self, id: str) -> bool:
        """
        Soft delete a user (marks as inactive).
        
        Args:
            id: User ID to delete
            
        Returns:
            True if user was deleted, False otherwise
        """
        try:
            collection = self._get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
            )
            
            if result.matched_count > 0:
                logger.info(f"Deleted user with ID: {id}")
                return True
            
            logger.warning(f"User not found for deletion with ID: {id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting user with ID {id}: {e}")
            raise
    
    async def exists(self, id: str) -> bool:
        """
        Check if a user exists.
        
        Args:
            id: User ID to check
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            collection = self._get_collection()
            doc = await collection.find_one({"_id": ObjectId(id)})
            return doc is not None
        except Exception as e:
            logger.error(f"Error checking user existence for ID {id}: {e}")
            raise
