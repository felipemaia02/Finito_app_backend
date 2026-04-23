"""Create Group use case."""

from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.entities.group_entity import Group
from app.models.group_schema import GroupCreate
from app.domain.interfaces.use_case import IUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class CreateGroupUseCase(IUseCase[GroupCreate, Group]):
    """Use case for creating a new group."""

    def __init__(self, repository: IGroupRepository):
        self.repository = repository

    async def execute(self, group_data: GroupCreate, creator_user_id: str) -> Group:
        try:
            logger.info(f"Creating group: {group_data.group_name}")
            group = Group(
                group_name=group_data.group_name,
                user_ids=[creator_user_id],
            )
            result = await self.repository.create(group)
            logger.info(f"Group created with ID: {result.id}")
            return result
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            raise
