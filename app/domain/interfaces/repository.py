"""
Base repository interface.
All repository implementations must follow this contract.
"""

from typing import Generic, TypeVar, Optional, List
from abc import ABC, abstractmethod

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Generic repository interface for CRUD operations.
    
    Type Parameters:
        T: The entity type this repository manages
    """
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Create a new entity.
        
        Args:
            entity: The entity to create
            
        Returns:
            The created entity with generated ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """
        Get an entity by its ID.
        
        Args:
            id: The entity ID
            
        Returns:
            The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get all entities with pagination.
        
        Args:
            skip: Number of entities to skip
            limit: Maximum number of entities to return
            
        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    async def update(self, id: str, entity: T) -> Optional[T]:
        """
        Update an existing entity.
        
        Args:
            id: The entity ID
            entity: The updated entity data
            
        Returns:
            The updated entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """
        Delete an entity by its ID.
        
        Args:
            id: The entity ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists(self, id: str) -> bool:
        """
        Check if an entity exists.
        
        Args:
            id: The entity ID
            
        Returns:
            True if exists, False otherwise
        """
        pass
