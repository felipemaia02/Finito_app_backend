"""Tests for controllers/expense_controller.py"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone
from bson import ObjectId
from app.controllers.expense_controller import ExpenseController
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.entities.expense_entity import Expense
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType
from app.models.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse


def make_mock_repo():
    return MagicMock(spec=IExpenseRepository)


def make_async_mock_repo():
    return AsyncMock(spec=IExpenseRepository)


def make_expense_response():
    return ExpenseResponse(
        id=str(ObjectId()),
        group_id="507f1f77bcf86cd799439012",
        amount_cents=5000,
        category=ExpenseCategory.ENTERTAINMENT,
        type_expense=ExpenseType.CREDIT_CARD,
        description="Movie tickets",
        spent_by="John Doe",
        date=datetime.now(timezone.utc),
        note="Weekend movie",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
    )


class TestExpenseControllerInitialization:
    """Test ExpenseController initialization"""

    def test_controller_creation(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert controller is not None

    def test_controller_stores_repository(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert controller.repository == mock_repo

    def test_controller_has_all_use_cases(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert controller.create_expense_use_case is not None
        assert controller.get_all_expenses_use_case is not None
        assert controller.get_expense_by_id_use_case is not None
        assert controller.update_expense_use_case is not None
        assert controller.delete_expense_use_case is not None
        assert controller.get_amounts_and_types_use_case is not None


class TestExpenseControllerMethods:
    """Test ExpenseController has all required methods"""

    def test_controller_has_create_expense_method(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, "create_expense")

    def test_controller_has_get_all_expenses_method(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, "get_all_expenses")

    def test_controller_has_get_expense_by_id_method(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, "get_expense_by_id")

    def test_controller_has_update_expense_method(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, "update_expense")

    def test_controller_has_delete_expense_method(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, "delete_expense")

    def test_controller_has_get_amounts_and_types_method(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, "get_amounts_and_types")

    def test_controller_methods_are_callable(self):
        mock_repo = make_mock_repo()
        controller = ExpenseController(mock_repo)
        assert callable(controller.create_expense)
        assert callable(controller.get_all_expenses)
        assert callable(controller.get_expense_by_id)
        assert callable(controller.update_expense)
        assert callable(controller.delete_expense)
        assert callable(controller.get_amounts_and_types)


class TestExpenseControllerCreateExpense:
    """Test create_expense method."""

    @pytest.mark.asyncio
    async def test_create_expense_success(self):
        mock_repo = make_async_mock_repo()

        # Must return a proper Expense entity since use case calls model_dump()
        from app.domain.entities.expense_entity import Expense

        expense_entity = Expense(
            group_id="507f1f77bcf86cd799439012",
            amount_cents=5000,
            category=ExpenseCategory.ENTERTAINMENT,
            type_expense=ExpenseType.CREDIT_CARD,
            spent_by="John Doe",
            date=datetime.now(timezone.utc),
        )
        expense_entity.id = str(ObjectId())
        mock_repo.create.return_value = expense_entity

        controller = ExpenseController(mock_repo)

        expense_data = ExpenseCreate(
            group_id="507f1f77bcf86cd799439012",
            amount_cents=5000,
            category=ExpenseCategory.ENTERTAINMENT,
            type_expense=ExpenseType.CREDIT_CARD,
            spent_by="John Doe",
        )

        result = await controller.create_expense(expense_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_create_expense_raises_on_error(self):
        mock_repo = make_async_mock_repo()
        mock_repo.create.side_effect = Exception("DB error")

        controller = ExpenseController(mock_repo)

        expense_data = ExpenseCreate(
            group_id="507f1f77bcf86cd799439012",
            amount_cents=5000,
            category=ExpenseCategory.ENTERTAINMENT,
            type_expense=ExpenseType.CREDIT_CARD,
            spent_by="John Doe",
        )

        with pytest.raises(Exception):
            await controller.create_expense(expense_data)


class TestExpenseControllerGetAllExpenses:
    """Test get_all_expenses method."""

    @pytest.mark.asyncio
    async def test_get_all_expenses_empty(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_all.return_value = []

        controller = ExpenseController(mock_repo)
        result = await controller.get_all_expenses("507f1f77bcf86cd799439012")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_expenses_with_pagination(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_all.return_value = []

        controller = ExpenseController(mock_repo)
        result = await controller.get_all_expenses(
            "507f1f77bcf86cd799439012", skip=5, limit=20
        )
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_all_expenses_raises_on_error(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_all.side_effect = Exception("DB error")

        controller = ExpenseController(mock_repo)

        with pytest.raises(Exception):
            await controller.get_all_expenses("507f1f77bcf86cd799439012")


class TestExpenseControllerGetExpenseById:
    """Test get_expense_by_id method."""

    @pytest.mark.asyncio
    async def test_get_expense_by_id_not_found(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_by_id.return_value = None

        controller = ExpenseController(mock_repo)
        result = await controller.get_expense_by_id(str(ObjectId()))
        assert result is None

    @pytest.mark.asyncio
    async def test_get_expense_by_id_raises_on_error(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_by_id.side_effect = Exception("DB error")

        controller = ExpenseController(mock_repo)

        with pytest.raises(Exception):
            await controller.get_expense_by_id(str(ObjectId()))


class TestExpenseControllerUpdateExpense:
    """Test update_expense method."""

    @pytest.mark.asyncio
    async def test_update_expense_not_found(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_by_id.return_value = None
        mock_repo.update.return_value = None

        controller = ExpenseController(mock_repo)

        expense_data = ExpenseUpdate(amount_cents=6000)
        result = await controller.update_expense(str(ObjectId()), expense_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_expense_raises_on_error(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_by_id.return_value = make_expense_response()
        mock_repo.update.side_effect = Exception("DB error")

        controller = ExpenseController(mock_repo)

        expense_data = ExpenseUpdate(amount_cents=6000)

        with pytest.raises(Exception):
            await controller.update_expense(str(ObjectId()), expense_data)


class TestExpenseControllerDeleteExpense:
    """Test delete_expense method."""

    @pytest.mark.asyncio
    async def test_delete_expense_success(self):
        mock_repo = make_async_mock_repo()
        mock_repo.delete.return_value = True

        controller = ExpenseController(mock_repo)
        result = await controller.delete_expense(str(ObjectId()))
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_expense_not_found(self):
        mock_repo = make_async_mock_repo()
        mock_repo.delete.return_value = False

        controller = ExpenseController(mock_repo)
        result = await controller.delete_expense(str(ObjectId()))
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_expense_raises_on_error(self):
        mock_repo = make_async_mock_repo()
        mock_repo.delete.side_effect = Exception("DB error")

        controller = ExpenseController(mock_repo)

        with pytest.raises(Exception):
            await controller.delete_expense(str(ObjectId()))


class TestExpenseControllerGetAmountsAndTypes:
    """Test get_amounts_and_types method."""

    @pytest.mark.asyncio
    async def test_get_amounts_and_types_empty(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_amounts_and_types.return_value = []

        controller = ExpenseController(mock_repo)
        result = await controller.get_amounts_and_types("507f1f77bcf86cd799439012")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_amounts_and_types_returns_data(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_amounts_and_types.return_value = [
            {"amount_cents": 1000, "type_expense": "cash"},
        ]

        controller = ExpenseController(mock_repo)
        result = await controller.get_amounts_and_types("507f1f77bcf86cd799439012")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_amounts_and_types_raises_on_error(self):
        mock_repo = make_async_mock_repo()
        mock_repo.get_amounts_and_types.side_effect = Exception("DB error")

        controller = ExpenseController(mock_repo)

        with pytest.raises(Exception):
            await controller.get_amounts_and_types("507f1f77bcf86cd799439012")
