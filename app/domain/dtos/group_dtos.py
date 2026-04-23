"""DTOs for group use case inputs."""

from typing import NamedTuple
from app.models.group_schema import GroupUpdate


class UpdateGroupInput(NamedTuple):
    group_id: str
    group_data: GroupUpdate


class AddUserToGroupInput(NamedTuple):
    group_id: str
    user_id: str


class RemoveUserFromGroupInput(NamedTuple):
    group_id: str
    user_id: str
