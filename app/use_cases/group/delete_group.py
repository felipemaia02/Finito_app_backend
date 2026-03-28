"""Delete Group use case."""

from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.interfaces.use_case import IUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class DeleteGroupUseCase(IUseCase[str, bool]):
    """Use case for soft-deleting a group."""

    def __init__(self, repository: IGroupRepository):
        self.repository = repository

    async def execute(self, group_id: str) -> bool:
        try:
            logger.info(f"Deleting group: {group_id}")
            result = await self.repository.delete(group_id)
            if not result:
                logger.warning(f"Group not found for deletion: {group_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting group {group_id}: {e}")
            raise
