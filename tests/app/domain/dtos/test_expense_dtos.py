"""Tests for domain/dtos/expense_dtos.py"""

import pytest
from app.domain.dtos.expense_dtos import GetAllExpensesInput, UpdateExpenseInput
from app.models.expense_schema import ExpenseUpdate
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType


class TestGetAllExpensesInput:
    """Test GetAllExpensesInput DTO"""

    def test_create_with_required_fields(self):
        """Test creating GetAllExpensesInput with required group_id"""
        dto = GetAllExpensesInput(group_id="group-123")
        assert dto.group_id == "group-123"

    def test_has_skip_field(self):
        """Test GetAllExpensesInput has skip field"""
        dto = GetAllExpensesInput(group_id="group-123", skip=10)
        assert dto.skip == 10

    def test_has_limit_field(self):
        """Test GetAllExpensesInput has limit field"""
        dto = GetAllExpensesInput(group_id="group-123", limit=20)
        assert dto.limit == 20

    def test_default_skip_value(self):
        """Test skip field has default value"""
        dto = GetAllExpensesInput(group_id="group-123")
        assert hasattr(dto, 'skip')

    def test_default_limit_value(self):
        """Test limit field has default value"""
        dto = GetAllExpensesInput(group_id="group-123")
        assert hasattr(dto, 'limit')

    def test_can_serialize(self):
        """Test GetAllExpensesInput can be serialized"""
        dto = GetAllExpensesInput(group_id="group-123", skip=5, limit=10)
        # NamedTuple has _asdict method
        data = dto._asdict()
        assert 'group_id' in data


class TestUpdateExpenseInput:
    """Test UpdateExpenseInput DTO"""

    def test_create_with_required_fields(self):
        """Test creating UpdateExpenseInput with required fields"""
        update_data = ExpenseUpdate(amount_cents=2000)
        dto = UpdateExpenseInput(
            expense_id="exp-123",
            expense_data=update_data
        )
        assert dto.expense_id == "exp-123"
        assert dto.expense_data == update_data

    def test_expense_id_field(self):
        """Test UpdateExpenseInput has expense_id field"""
        update_data = ExpenseUpdate(amount_cents=1000)
        dto = UpdateExpenseInput(
            expense_id="exp-456",
            expense_data=update_data
        )
        assert dto.expense_id == "exp-456"

    def test_expense_data_field(self):
        """Test UpdateExpenseInput has expense_data field"""
        update_data = ExpenseUpdate(category=ExpenseCategory.GROCERIES, note="Dinner")
        dto = UpdateExpenseInput(
            expense_id="exp-789",
            expense_data=update_data
        )
        assert dto.expense_data == update_data

    def test_expense_data_with_multiple_fields(self):
        """Test expense_data field with multiple update fields"""
        update_data = ExpenseUpdate(amount_cents=1000, note="Updated", spent_by="Jane")
        dto = UpdateExpenseInput(expense_id="exp", expense_data=update_data)
        assert dto.expense_data == update_data

    def test_can_serialize(self):
        """Test UpdateExpenseInput can be serialized"""
        update_data = ExpenseUpdate(amount_cents=1500)
        dto = UpdateExpenseInput(
            expense_id="exp-123",
            expense_data=update_data
        )
        # NamedTuple has _asdict method
        data = dto._asdict()
        assert "expense_id" in data
