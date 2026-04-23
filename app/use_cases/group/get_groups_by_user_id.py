"""Get Groups By User ID use case."""

from typing import List
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.entities.group_entity import Group
from app.domain.interfaces.use_case import IUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class GetGroupsByUserIdUseCase(IUseCase[str, List[Group]]):
    """Use case for retrieving all groups a user belongs to."""

    def __init__(self, repository: IGroupRepository):
        self.repository = repository

    async def execute(self, user_id: str) -> List[Group]:
        try:
            logger.info(f"Fetching groups for user: {user_id}")
            result = await self.repository.get_by_user_id(user_id)
            logger.info(f"Found {len(result)} groups for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error fetching groups for user {user_id}: {e}")
            raise
