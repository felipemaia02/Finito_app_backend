"""Dependency injection container for group operations."""

from fastapi import Depends
from app.controllers.group_controller import GroupController
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.infrastructure.repositories.group_repository import MongoGroupRepository
from app.infrastructure.repositories.user_repository import MongoUserRepository


class GroupDependencies:
    """Container for managing group-related dependencies."""

    @staticmethod
    def get_group_repository() -> IGroupRepository:
        return MongoGroupRepository()

    @staticmethod
    def get_user_repository() -> IUserRepository:
        return MongoUserRepository()

    @staticmethod
    def get_controller(
        group_repository: IGroupRepository = Depends(get_group_repository.__func__),
        user_repository: IUserRepository = Depends(get_user_repository.__func__),
    ) -> GroupController:
        return GroupController(
            group_repository=group_repository,
            user_repository=user_repository,
        )
