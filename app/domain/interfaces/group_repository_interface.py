"""Group repository interface."""

from app.domain.interfaces.repository import BaseRepository
from app.domain.entities.group_entity import Group


class IGroupRepository(BaseRepository[Group]):
    """
    Interface for group repository operations.
    Extends the base repository with group CRUD operations.
    The base class already provides: create, get_by_id, get_all, update, delete, exists.
    """

    pass
