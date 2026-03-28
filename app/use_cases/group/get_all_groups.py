"""Get All Groups use case."""

from typing import List
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.entities.group_entity import Group
from app.domain.interfaces.use_case import IUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class GetAllGroupsUseCase(IUseCase[None, List[Group]]):
    """Use case for retrieving all groups."""

    def __init__(self, repository: IGroupRepository):
        self.repository = repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[Group]:
        try:
            logger.info(f"Fetching all groups (skip={skip}, limit={limit})")
            result = await self.repository.get_all(skip=skip, limit=limit)
            logger.info(f"Found {len(result)} groups")
            return result
        except Exception as e:
            logger.error(f"Error fetching groups: {e}")
            raise
