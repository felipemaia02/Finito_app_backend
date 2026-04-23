"""Group controller — orchestrates use cases and builds GroupResponse with populated users."""

from typing import List, Optional
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.entities.group_entity import Group
from app.models.group_schema import GroupCreate, GroupUpdate, GroupResponse, GroupMemberResponse
from app.domain.dtos.group_dtos import UpdateGroupInput, AddUserToGroupInput, RemoveUserFromGroupInput
from app.use_cases.group.create_group import CreateGroupUseCase
from app.use_cases.group.get_all_groups import GetAllGroupsUseCase
from app.use_cases.group.get_group_by_id import GetGroupByIdUseCase
from app.use_cases.group.update_group import UpdateGroupUseCase
from app.use_cases.group.delete_group import DeleteGroupUseCase
from app.use_cases.group.add_user_to_group import AddUserToGroupUseCase
from app.use_cases.group.remove_user_from_group import RemoveUserFromGroupUseCase
from app.use_cases.group.get_groups_by_user_id import GetGroupsByUserIdUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class GroupController:
    """Orchestrates group use cases and populates user data in responses."""

    def __init__(
        self,
        group_repository: IGroupRepository,
        user_repository: IUserRepository,
    ):
        self.user_repository = user_repository
        self.create_group_use_case = CreateGroupUseCase(group_repository)
        self.get_all_groups_use_case = GetAllGroupsUseCase(group_repository)
        self.get_group_by_id_use_case = GetGroupByIdUseCase(group_repository)
        self.update_group_use_case = UpdateGroupUseCase(group_repository)
        self.delete_group_use_case = DeleteGroupUseCase(group_repository)
        self.add_user_to_group_use_case = AddUserToGroupUseCase(group_repository)
        self.remove_user_from_group_use_case = RemoveUserFromGroupUseCase(group_repository)
        self.get_groups_by_user_id_use_case = GetGroupsByUserIdUseCase(group_repository)

    async def _build_response(self, group: Group) -> GroupResponse:
        """Build GroupResponse with populated user objects from user_ids."""
        users = []
        for user_id in group.user_ids:
            user = await self.user_repository.get_by_id(user_id)
            if user:
                users.append(GroupMemberResponse(id=user.id, name=user.name))
        return GroupResponse(
            id=group.id,
            group_name=group.group_name,
            users=users,
            created_at=group.created_at,
            updated_at=group.updated_at,
        )

    async def _require_membership(self, group: Group, user_email: str) -> None:
        """Raise PermissionError if the user is not a member of the group."""
        user = await self.user_repository.get_by_email(user_email)
        if user is None or user.id not in group.user_ids:
            raise PermissionError("You are not a member of this group")

    async def create_group(self, group_data: GroupCreate, creator_email: str) -> GroupResponse:
        creator = await self.user_repository.get_by_email(creator_email)
        creator_user_id = creator.id if creator else None
        group = await self.create_group_use_case.execute(group_data, creator_user_id)
        return await self._build_response(group)

    async def get_all_groups(
        self, skip: int = 0, limit: int = 100
    ) -> List[GroupResponse]:
        """Return all groups."""
        groups = await self.get_all_groups_use_case.execute(skip=skip, limit=limit)
        return [await self._build_response(g) for g in groups]

    async def get_group_by_id(self, group_id: str, user_email: str) -> Optional[GroupResponse]:
        group = await self.get_group_by_id_use_case.execute(group_id)
        if group is None:
            return None
        await self._require_membership(group, user_email)
        return await self._build_response(group)

    async def update_group(
        self, group_id: str, group_data: GroupUpdate, user_email: str
    ) -> Optional[GroupResponse]:
        group = await self.get_group_by_id_use_case.execute(group_id)
        if group is None:
            return None
        await self._require_membership(group, user_email)
        updated = await self.update_group_use_case.execute(
            UpdateGroupInput(group_id=group_id, group_data=group_data)
        )
        if updated is None:
            return None
        return await self._build_response(updated)

    async def delete_group(self, group_id: str, user_email: str) -> bool:
        group = await self.get_group_by_id_use_case.execute(group_id)
        if group is None:
            return False
        user = await self.user_repository.get_by_email(user_email)
        if user is None or group.creator_id != user.id:
            raise PermissionError("Only the group creator can delete the group")
        return await self.delete_group_use_case.execute(group_id)

    async def get_groups_by_user_email(self, user_email: str) -> List[GroupResponse]:
        user = await self.user_repository.get_by_email(user_email)
        if user is None:
            return []
        groups = await self.get_groups_by_user_id_use_case.execute(user.id)
        return [await self._build_response(g) for g in groups]

    async def add_user_to_group(
        self, group_id: str, user_id: str, requester_email: str
    ) -> Optional[GroupResponse]:
        group = await self.get_group_by_id_use_case.execute(group_id)
        if group is None:
            return None
        await self._require_membership(group, requester_email)
        updated = await self.add_user_to_group_use_case.execute(
            AddUserToGroupInput(group_id=group_id, user_id=user_id)
        )
        if updated is None:
            return None
        return await self._build_response(updated)

    async def remove_user_from_group(
        self, group_id: str, user_id: str, requester_email: str
    ) -> Optional[GroupResponse]:
        group = await self.get_group_by_id_use_case.execute(group_id)
        if group is None:
            return None
        await self._require_membership(group, requester_email)
        updated = await self.remove_user_from_group_use_case.execute(
            RemoveUserFromGroupInput(group_id=group_id, user_id=user_id)
        )
        if updated is None:
            return None
        return await self._build_response(updated)
