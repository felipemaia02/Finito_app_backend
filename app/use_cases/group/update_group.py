"""Update Group use case."""

from typing import Optional
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.entities.group_entity import Group
from app.domain.dtos.group_dtos import UpdateGroupInput
from app.domain.interfaces.use_case import IUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class UpdateGroupUseCase(IUseCase[UpdateGroupInput, Optional[Group]]):
    """Use case for updating a group's data."""

    def __init__(self, repository: IGroupRepository):
        self.repository = repository

    async def execute(self, input_data: UpdateGroupInput) -> Optional[Group]:
        try:
            logger.info(f"Updating group: {input_data.group_id}")
            group = await self.repository.get_by_id(input_data.group_id)
            if group is None:
                logger.warning(f"Group not found for update: {input_data.group_id}")
                return None

            update_fields = input_data.group_data.model_dump(exclude_unset=True)
            for field, value in update_fields.items():
                setattr(group, field, value)
            group.update_timestamp()

            result = await self.repository.update(input_data.group_id, group)
            logger.info(f"Group updated: {input_data.group_id}")
            return result
        except Exception as e:
            logger.error(f"Error updating group {input_data.group_id}: {e}")
            raise
