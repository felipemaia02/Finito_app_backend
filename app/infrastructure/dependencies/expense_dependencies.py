"""Dependency injection container for expense operations."""

from fastapi import Depends

from app.controllers.expense_controller import ExpenseController
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.infrastructure.repositories.expense_repository import MongoExpenseRepository
from app.infrastructure.repositories.group_repository import MongoGroupRepository
from app.infrastructure.repositories.user_repository import MongoUserRepository


class ExpenseDependencies:
    """Container for managing expense-related dependencies."""

    @staticmethod
    def get_repository() -> IExpenseRepository:
        return MongoExpenseRepository()

    @staticmethod
    def get_group_repository() -> IGroupRepository:
        return MongoGroupRepository()

    @staticmethod
    def get_user_repository() -> IUserRepository:
        return MongoUserRepository()

    @staticmethod
    def get_controller(
        repository: IExpenseRepository = Depends(get_repository.__func__),
        group_repository: IGroupRepository = Depends(get_group_repository.__func__),
        user_repository: IUserRepository = Depends(get_user_repository.__func__),
    ) -> ExpenseController:
        return ExpenseController(repository, group_repository, user_repository)
