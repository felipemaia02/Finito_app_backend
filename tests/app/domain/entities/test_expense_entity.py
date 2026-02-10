"""Tests for domain/entities/expense_entity.py"""

from datetime import datetime, timezone
import pytest
from app.domain.entities.expense_entity import Expense
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType


class TestExpenseEntityInitialization:
    """Test Expense entity initialization"""

    def test_expense_creation_required_fields(self):
        """Test creating Expense with all required fields"""
        expense = Expense(
            group_id="group-123",
            amount_cents=2500,
            category=ExpenseCategory.GROCERIES,
            type_expense=ExpenseType.CASH,
            spent_by="John Doe"
        )
        assert expense.group_id == "group-123"
        assert expense.amount_cents == 2500
        assert expense.category == ExpenseCategory.GROCERIES
        assert expense.type_expense == ExpenseType.CASH
        assert expense.spent_by == "John Doe"

    def test_expense_creation_with_note(self):
        """Test creating Expense with optional note"""
        expense = Expense(
            group_id="group-123",
            amount_cents=1500,
            category=ExpenseCategory.RESTAURANTS,
            type_expense=ExpenseType.CREDIT_CARD,
            spent_by="Jane",
            note="Lunch with team"
        )
        assert expense.note == "Lunch with team"

    def test_expense_creation_without_note(self):
        """Test creating Expense without note defaults to None"""
        expense = Expense(
            group_id="group-123",
            amount_cents=1000,
            category=ExpenseCategory.UTILITIES,
            type_expense=ExpenseType.DEBIT_CARD,
            spent_by="Admin"
        )
        assert expense.note is None

    def test_expense_has_is_deleted_field(self):
        """Test Expense has is_deleted field defaulting to False"""
        expense = Expense(
            group_id="group-123",
            amount_cents=1000,
            category=ExpenseCategory.SHOPPING,
            type_expense=ExpenseType.PIX_TRANSFER,
            spent_by="User"
        )
        assert hasattr(expense, 'is_deleted')
        assert expense.is_deleted is False

    def test_expense_creation_with_explicit_is_deleted(self):
        """Test creating Expense with explicit is_deleted value"""
        expense = Expense(
            group_id="group-123",
            amount_cents=1000,
            category=ExpenseCategory.ENTERTAINMENT,
            type_expense=ExpenseType.CASH,
            spent_by="User",
            is_deleted=True
        )
        assert expense.is_deleted is True


class TestExpenseEntityValidation:
    """Test Expense entity validation"""

    def test_expense_requires_group_id(self):
        """Test Expense requires group_id"""
        with pytest.raises(ValueError):
            Expense(
                group_id="",  # Empty string should fail
                amount_cents=1000,
                category=ExpenseCategory.GROCERIES,
                type_expense=ExpenseType.CASH,
                spent_by="User"
            )

    def test_expense_requires_positive_amount(self):
        """Test Expense requires positive amount_cents"""
        with pytest.raises(ValueError):
            Expense(
                group_id="group-123",
                amount_cents=0,  # Must be > 0
                category=ExpenseCategory.GROCERIES,
                type_expense=ExpenseType.CASH,
                spent_by="User"
            )

    def test_expense_requires_spent_by_with_min_length(self):
        """Test Expense requires non-empty spent_by"""
        with pytest.raises(ValueError):
            Expense(
                group_id="group-123",
                amount_cents=1000,
                category=ExpenseCategory.GROCERIES,
                type_expense=ExpenseType.CASH,
                spent_by=""  # Must have length >= 1
            )

    def test_expense_note_max_length(self):
        """Test Expense note has maximum length"""
        with pytest.raises(ValueError):
            Expense(
                group_id="group-123",
                amount_cents=1000,
                category=ExpenseCategory.GROCERIES,
                type_expense=ExpenseType.CASH,
                spent_by="User",
                note="x" * 501  # Max 500 chars
            )


class TestExpenseEntityInheritance:
    """Test Expense inherits from BaseEntity"""

    def test_expense_has_id_field(self):
        """Test Expense inherits id field from BaseEntity"""
        expense = Expense(
            id="expense-123",
            group_id="group-123",
            amount_cents=1000,
            category=ExpenseCategory.GROCERIES,
            type_expense=ExpenseType.CASH,
            spent_by="User"
        )
        assert expense.id == "expense-123"

    def test_expense_has_timestamps(self):
        """Test Expense inherits timestamps from BaseEntity"""
        expense = Expense(
            group_id="group-123",
            amount_cents=1000,
            category=ExpenseCategory.GROCERIES,
            type_expense=ExpenseType.CASH,
            spent_by="User"
        )
        assert hasattr(expense, 'created_at')
        assert hasattr(expense, 'updated_at')
        assert isinstance(expense.created_at, datetime)
        assert isinstance(expense.updated_at, datetime)

    def test_expense_has_update_timestamp_method(self):
        """Test Expense inherits update_timestamp method"""
        expense = Expense(
            group_id="group-123",
            amount_cents=1000,
            category=ExpenseCategory.GROCERIES,
            type_expense=ExpenseType.CASH,
            spent_by="User"
        )
        original_updated = expense.updated_at
        expense.update_timestamp()
        assert expense.updated_at >= original_updated


class TestExpenseEntityAllCategories:
    """Test Expense works with all expense categories"""

    def test_expense_with_transportation(self):
        """Test Expense with TRANSPORTATION category"""
        expense = Expense(
            group_id="g",
            amount_cents=1000,
            category=ExpenseCategory.TRANSPORTATION,
            type_expense=ExpenseType.CASH,
            spent_by="U"
        )
        assert expense.category == ExpenseCategory.TRANSPORTATION

    def test_expense_with_groceries(self):
        """Test Expense with GROCERIES category"""
        expense = Expense(
            group_id="g",
            amount_cents=5000,
            category=ExpenseCategory.GROCERIES,
            type_expense=ExpenseType.CREDIT_CARD,
            spent_by="U"
        )
        assert expense.category == ExpenseCategory.GROCERIES


class TestExpenseEntityAllTypes:
    """Test Expense works with all payment types"""

    def test_expense_with_cash(self):
        """Test Expense with CASH payment type"""
        expense = Expense(
            group_id="g",
            amount_cents=1000,
            category=ExpenseCategory.GROCERIES,
            type_expense=ExpenseType.CASH,
            spent_by="U"
        )
        assert expense.type_expense == ExpenseType.CASH

    def test_expense_with_credit_card(self):
        """Test Expense with CREDIT_CARD payment type"""
        expense = Expense(
            group_id="g",
            amount_cents=2000,
            category=ExpenseCategory.RESTAURANTS,
            type_expense=ExpenseType.CREDIT_CARD,
            spent_by="U"
        )
        assert expense.type_expense == ExpenseType.CREDIT_CARD

    def test_expense_with_debit_card(self):
        """Test Expense with DEBIT_CARD payment type"""
        expense = Expense(
            group_id="g",
            amount_cents=1500,
            category=ExpenseCategory.UTILITIES,
            type_expense=ExpenseType.DEBIT_CARD,
            spent_by="U"
        )
        assert expense.type_expense == ExpenseType.DEBIT_CARD

    def test_expense_with_pix_transfer(self):
        """Test Expense with PIX_TRANSFER payment type"""
        expense = Expense(
            group_id="g",
            amount_cents=3000,
            category=ExpenseCategory.ENTERTAINMENT,
            type_expense=ExpenseType.PIX_TRANSFER,
            spent_by="U"
        )
        assert expense.type_expense == ExpenseType.PIX_TRANSFER
