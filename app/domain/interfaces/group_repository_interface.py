"""Group repository interface."""

from abc import abstractmethod
from typing import List
from app.domain.interfaces.repository import BaseRepository
from app.domain.entities.group_entity import Group


class IGroupRepository(BaseRepository[Group]):
    """
    Interface for group repository operations.
    Extends the base repository with group CRUD operations.
    The base class already provides: create, get_by_id, get_all, update, delete, exists.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Group]:
        """Return all groups that a given user belongs to."""
        ...
