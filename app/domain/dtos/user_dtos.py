"""Data Transfer Objects for User use cases."""

from typing import NamedTuple
from app.models.user_schema import UserUpdate


class GetAllUsersInput(NamedTuple):
    """Input data for GetAllUsersUseCase."""

    skip: int = 0
    limit: int = 100


class UpdateUserInput(NamedTuple):
    """Input data for UpdateUserUseCase."""

    user_id: str
    user_data: UserUpdate


class GetUserByEmailInput(NamedTuple):
    """Input data for GetUserByEmailUseCase."""

    email: str
