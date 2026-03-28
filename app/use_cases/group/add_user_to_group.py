"""Add User to Group use case."""

from typing import Optional
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.entities.group_entity import Group
from app.domain.dtos.group_dtos import AddUserToGroupInput
from app.domain.interfaces.use_case import IUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class AddUserToGroupUseCase(IUseCase[AddUserToGroupInput, Optional[Group]]):
    """Use case for adding a user to a group."""

    def __init__(self, repository: IGroupRepository):
        self.repository = repository

    async def execute(self, input_data: AddUserToGroupInput) -> Optional[Group]:
        try:
            logger.info(
                f"Adding user {input_data.user_id} to group {input_data.group_id}"
            )
            group = await self.repository.get_by_id(input_data.group_id)
            if group is None:
                logger.warning(f"Group not found: {input_data.group_id}")
                return None

            if input_data.user_id in group.user_ids:
                raise ValueError(
                    f"User {input_data.user_id} is already a member of this group"
                )

            group.user_ids.append(input_data.user_id)
            group.update_timestamp()
            result = await self.repository.update(group.id, group)
            logger.info(
                f"User {input_data.user_id} added to group {input_data.group_id}"
            )
            return result
        except ValueError as ve:
            logger.warning(f"Validation error adding user to group: {ve}")
            raise
        except Exception as e:
            logger.error(
                f"Error adding user {input_data.user_id} to group {input_data.group_id}: {e}"
            )
            raise
