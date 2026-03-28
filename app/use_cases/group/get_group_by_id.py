"""Get Group By ID use case."""

from typing import Optional
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.entities.group_entity import Group
from app.domain.interfaces.use_case import IUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class GetGroupByIdUseCase(IUseCase[str, Optional[Group]]):
    """Use case for retrieving a group by its ID."""

    def __init__(self, repository: IGroupRepository):
        self.repository = repository

    async def execute(self, group_id: str) -> Optional[Group]:
        try:
            logger.info(f"Fetching group by ID: {group_id}")
            result = await self.repository.get_by_id(group_id)
            if result is None:
                logger.warning(f"Group not found: {group_id}")
            return result
        except Exception as e:
            logger.error(f"Error fetching group {group_id}: {e}")
            raise
