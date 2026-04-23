"""Remove User from Group use case."""

from typing import Optional
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.entities.group_entity import Group
from app.domain.dtos.group_dtos import RemoveUserFromGroupInput
from app.domain.interfaces.use_case import IUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class RemoveUserFromGroupUseCase(IUseCase[RemoveUserFromGroupInput, Optional[Group]]):
    """Use case for removing a user from a group."""

    def __init__(self, repository: IGroupRepository):
        self.repository = repository

    async def execute(self, input_data: RemoveUserFromGroupInput) -> Optional[Group]:
        try:
            logger.info(
                f"Removing user {input_data.user_id} from group {input_data.group_id}"
            )
            group = await self.repository.get_by_id(input_data.group_id)
            if group is None:
                logger.warning(f"Group not found: {input_data.group_id}")
                return None

            if input_data.user_id not in group.user_ids:
                raise ValueError(
                    f"User {input_data.user_id} is not a member of this group"
                )

            group.user_ids.remove(input_data.user_id)
            group.update_timestamp()
            result = await self.repository.update(group.id, group)
            logger.info(
                f"User {input_data.user_id} removed from group {input_data.group_id}"
            )
            return result
        except ValueError as ve:
            logger.warning(f"Validation error removing user from group: {ve}")
            raise
        except Exception as e:
            logger.error(
                f"Error removing user {input_data.user_id} from group {input_data.group_id}: {e}"
            )
            raise
