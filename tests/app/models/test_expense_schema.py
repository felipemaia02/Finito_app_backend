"""Tests for models/expense_schema.py"""

import pytest
from app.models.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType


class TestExpenseCreateSchema:
    """Test ExpenseCreate Pydantic schema"""

    def test_create_with_required_fields(self):
        """Test creating ExpenseCreate with required fields"""
        schema = ExpenseCreate(
            group_id="group-123",
            amount_cents=2500,
            category=ExpenseCategory.GROCERIES,
            type_expense=ExpenseType.CASH,
            spent_by="John"
        )
        assert schema.group_id == "group-123"
        assert schema.amount_cents == 2500

    def test_create_with_note(self):
        """Test ExpenseCreate with optional note"""
        schema = ExpenseCreate(
            group_id="g",
            amount_cents=1000,
            category=ExpenseCategory.RESTAURANTS,
            type_expense=ExpenseType.CREDIT_CARD,
            spent_by="Jane",
            note="Lunch"
        )
        assert schema.note == "Lunch"

    def test_create_validation_negative_amount(self):
        """Test ExpenseCreate validates amount must be positive"""
        with pytest.raises(ValueError):
            ExpenseCreate(
                group_id="g",
                amount_cents=-100,
                category=ExpenseCategory.GROCERIES,
                type_expense=ExpenseType.CASH,
                spent_by="U"
            )

    def test_create_can_serialize(self):
        """Test ExpenseCreate can be serialized"""
        schema = ExpenseCreate(
            group_id="g",
            amount_cents=1500,
            category=ExpenseCategory.UTILITIES,
            type_expense=ExpenseType.DEBIT_CARD,
            spent_by="A"
        )
        data = schema.model_dump()
        assert "group_id" in data
        assert "amount_cents" in data


class TestExpenseUpdateSchema:
    """Test ExpenseUpdate Pydantic schema"""

    def test_update_with_partial_data(self):
        """Test ExpenseUpdate allows partial updates"""
        schema = ExpenseUpdate(amount_cents=2000)
        assert schema.amount_cents == 2000

    def test_update_with_all_fields(self):
        """Test ExpenseUpdate with all optional fields"""
        schema = ExpenseUpdate(
            amount_cents=3000,
            category=ExpenseCategory.ENTERTAINMENT,
            type_expense=ExpenseType.PIX_TRANSFER,
            spent_by="Bob",
            note="Updated note"
        )
        assert schema.amount_cents == 3000
        assert schema.category == ExpenseCategory.ENTERTAINMENT
        assert schema.note == "Updated note"

    def test_update_with_empty_data(self):
        """Test ExpenseUpdate can be created with no fields"""
        schema = ExpenseUpdate()
        # Should work as all fields are optional
        assert True

    def test_update_can_serialize(self):
        """Test ExpenseUpdate can be serialized"""
        schema = ExpenseUpdate(category=ExpenseCategory.SHOPPING)
        data = schema.model_dump(exclude_unset=True)
        assert "category" in data


class TestExpenseResponseSchema:
    """Test ExpenseResponse Pydantic schema"""

    def test_response_with_required_fields(self):
        """Test creating ExpenseResponse with all fields"""
        response = ExpenseResponse(
            id="exp-123",
            group_id="group-456",
            amount_cents=1500,
            category=ExpenseCategory.GROCERIES,
            type_expense=ExpenseType.CASH,
            spent_by="User",
            date="2026-02-10T00:00:00Z",
            created_at="2026-02-10T00:00:00Z",
            updated_at="2026-02-10T00:00:00Z"
        )
        assert response.id == "exp-123"
        assert response.group_id == "group-456"

    def test_response_can_include_note(self):
        """Test ExpenseResponse can include optional note"""
        response = ExpenseResponse(
            id="exp",
            group_id="g",
            amount_cents=1000,
            category=ExpenseCategory.RESTAURANTS,
            type_expense=ExpenseType.CREDIT_CARD,
            spent_by="Jane",
            note="Dinner note",
            date="2026-02-10T00:00:00Z",
            created_at="2026-02-10T00:00:00Z",
            updated_at="2026-02-10T00:00:00Z"
        )
        assert response.note == "Dinner note"

    def test_response_can_serialize_to_json(self):
        """Test ExpenseResponse can be serialized to JSON"""
        response = ExpenseResponse(
            id="exp-789",
            group_id="g-789",
            amount_cents=2500,
            category=ExpenseCategory.UTILITIES,
            type_expense=ExpenseType.DEBIT_CARD,
            spent_by="Admin",
            date="2026-02-10T00:00:00Z",
            created_at="2026-02-10T00:00:00Z",
            updated_at="2026-02-10T00:00:00Z"
        )
        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        assert "exp-789" in json_str

    def test_response_to_dict(self):
        """Test ExpenseResponse to dictionary"""
        response = ExpenseResponse(
            id="resp-1",
            group_id="g1",
            amount_cents=1000,
            category=ExpenseCategory.ENTERTAINMENT,
            type_expense=ExpenseType.PIX_TRANSFER,
            spent_by="X",
            date="2026-02-10T00:00:00Z",
            created_at="2026-02-10T00:00:00Z",
            updated_at="2026-02-10T00:00:00Z"
        )
        data = response.model_dump()
        assert data['id'] == "resp-1"
        assert data['amount_cents'] == 1000
