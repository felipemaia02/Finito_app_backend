"""Tests for expense_category_enum.py and expense_type_enum.py"""

import pytest
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType


class TestExpenseCategoryEnumValues:
    """Test ExpenseCategory enum values"""

    def test_category_transportation(self):
        """Test TRANSPORTATION category"""
        assert ExpenseCategory.TRANSPORTATION.value == "transportation"
        assert ExpenseCategory.TRANSPORTATION.name == "TRANSPORTATION"

    def test_category_entertainment(self):
        """Test ENTERTAINMENT category"""
        assert ExpenseCategory.ENTERTAINMENT.value == "entertainment"

    def test_category_utilities(self):
        """Test UTILITIES category"""
        assert ExpenseCategory.UTILITIES.value == "utilities"

    def test_category_healthcare(self):
        """Test HEALTHCARE category"""
        assert ExpenseCategory.HEALTHCARE.value == "healthcare"

    def test_category_education(self):
        """Test EDUCATION category"""
        assert ExpenseCategory.EDUCATION.value == "education"

    def test_category_shopping(self):
        """Test SHOPPING category"""
        assert ExpenseCategory.SHOPPING.value == "shopping"

    def test_all_categories_have_values(self):
        """Test all categories have non-empty string values"""
        for category in ExpenseCategory:
            assert isinstance(category.value, str)
            assert len(category.value) > 0

    def test_all_categories_are_strings(self):
        """Test all category values are strings"""
        for category in ExpenseCategory:
            assert isinstance(category.value, str)

    def test_category_count(self):
        """Test there are 21 expense categories"""
        categories = list(ExpenseCategory)
        assert len(categories) == 21

    def test_categories_unique_values(self):
        """Test all categories have unique values"""
        values = [cat.value for cat in ExpenseCategory]
        assert len(values) == len(set(values))

    def test_categories_unique_names(self):
        """Test all categories have unique names"""
        names = [cat.name for cat in ExpenseCategory]
        assert len(names) == len(set(names))
    def test_categories_unique_names(self):
        """Test all categories have unique names"""
        names = [cat.name for cat in ExpenseCategory]
        assert len(names) == len(set(names))


class TestExpenseCategoryEnumComparison:
    """Test ExpenseCategory enum comparisons"""

    def test_category_equality(self):
        """Test category equality comparison"""
        assert ExpenseCategory.UTILITIES == ExpenseCategory.UTILITIES
        assert ExpenseCategory.UTILITIES != ExpenseCategory.TRANSPORTATION

    def test_category_string_representation(self):
        """Test category string representation"""
        category = ExpenseCategory.UTILITIES
        assert str(category) == "utilities"

    def test_category_from_value(self):
        """Test getting category from string value"""
        category = ExpenseCategory("utilities")
        assert category == ExpenseCategory.UTILITIES

    def test_category_iteration(self):
        """Test iterating over all categories"""
        categories = list(ExpenseCategory)
        assert len(categories) > 0
        assert all(isinstance(cat, ExpenseCategory) for cat in categories)

    def test_category_members(self):
        """Test getting specific category members"""
        # Test some key categories exist
        assert hasattr(ExpenseCategory, 'UTILITIES')
        assert hasattr(ExpenseCategory, 'RESTAURANTS')
        assert hasattr(ExpenseCategory, 'ENTERTAINMENT')


class TestExpenseCategoryEnumBehavior:
    """Test ExpenseCategory enum behavior"""

    def test_category_is_enum_instance(self):
        """Test category instances are enum instances"""
        category = ExpenseCategory.UTILITIES
        assert isinstance(category, ExpenseCategory)

    def test_category_has_name_attribute(self):
        """Test category has name attribute"""
        assert hasattr(ExpenseCategory.UTILITIES, 'name')
        assert ExpenseCategory.UTILITIES.name == 'UTILITIES'

    def test_category_has_value_attribute(self):
        """Test category has value attribute"""
        assert hasattr(ExpenseCategory.UTILITIES, 'value')
        assert ExpenseCategory.UTILITIES.value == 'utilities'

    def test_category_callable_from_value(self):
        """Test category can be instantiated from value"""
        cat1 = ExpenseCategory("utilities")
        cat2 = ExpenseCategory.UTILITIES
        assert cat1 == cat2

    def test_category_invalid_value_raises_error(self):
        """Test invalid category value raises error"""
        with pytest.raises(ValueError):
            ExpenseCategory("invalid_category")

    def test_category_name_to_value_mapping(self):
        """Test name to value mapping for categories"""
        for category in ExpenseCategory:
            retrieved = ExpenseCategory[category.name]
            assert retrieved == category


class TestExpenseTypeEnumValues:
    """Test ExpenseType enum values"""

    def test_type_cash(self):
        """Test CASH type exists and has correct value"""
        assert ExpenseType.CASH.value == "cash"
        assert ExpenseType.CASH.name == "CASH"

    def test_type_credit_card(self):
        """Test CREDIT_CARD type exists and has correct value"""
        assert ExpenseType.CREDIT_CARD.value == "credit_card"
        assert ExpenseType.CREDIT_CARD.name == "CREDIT_CARD"

    def test_type_debit_card(self):
        """Test DEBIT_CARD type exists"""
        assert ExpenseType.DEBIT_CARD.value == "debit_card"

    def test_type_pix_transfer(self):
        """Test PIX_TRANSFER type exists"""
        assert ExpenseType.PIX_TRANSFER.value == "pix_transfer"

    def test_all_types_have_values(self):
        """Test all types have non-empty string values"""
        for exp_type in ExpenseType:
            assert isinstance(exp_type.value, str)
            assert len(exp_type.value) > 0

    def test_type_count(self):
        """Test there are exactly 4 expense types"""
        types_list = list(ExpenseType)
        assert len(types_list) == 4

    def test_types_unique_values(self):
        """Test all types have unique values"""
        values = [t.value for t in ExpenseType]
        assert len(values) == len(set(values))

    def test_types_unique_names(self):
        """Test all types have unique names"""
        names = [t.name for t in ExpenseType]
        assert len(names) == len(set(names))


class TestExpenseTypeEnumComparison:
    """Test ExpenseType enum comparisons"""

    def test_type_equality(self):
        """Test type equality comparison"""
        assert ExpenseType.CASH == ExpenseType.CASH
        assert ExpenseType.CASH != ExpenseType.CREDIT_CARD

    def test_type_string_representation(self):
        """Test type string representation"""
        exp_type = ExpenseType.CASH
        assert str(exp_type) == "cash"

    def test_type_from_value(self):
        """Test getting type from string value"""
        exp_type = ExpenseType("cash")
        assert exp_type == ExpenseType.CASH

    def test_type_iteration(self):
        """Test iterating over all types"""
        types_list = list(ExpenseType)
        assert len(types_list) == 4
        assert all(isinstance(t, ExpenseType) for t in types_list)

    def test_type_members(self):
        """Test getting specific type members"""
        assert hasattr(ExpenseType, 'CASH')
        assert hasattr(ExpenseType, 'CREDIT_CARD')
        assert hasattr(ExpenseType, 'DEBIT_CARD')
        assert hasattr(ExpenseType, 'PIX_TRANSFER')


class TestExpenseTypeEnumBehavior:
    """Test ExpenseType enum behavior"""

    def test_type_is_enum_instance(self):
        """Test type instances are enum instances"""
        exp_type = ExpenseType.CASH
        assert isinstance(exp_type, ExpenseType)

    def test_type_has_name_attribute(self):
        """Test type has name attribute"""
        assert hasattr(ExpenseType.CASH, 'name')
        assert ExpenseType.CASH.name == 'CASH'

    def test_type_has_value_attribute(self):
        """Test type has value attribute"""
        assert hasattr(ExpenseType.CASH, 'value')
        assert ExpenseType.CASH.value == 'cash'

    def test_type_str_method(self):
        """Test type __str__ method returns value"""
        exp_type = ExpenseType.CASH
        assert str(exp_type) == "cash"

    def test_type_callable_from_value(self):
        """Test type can be instantiated from value"""
        t1 = ExpenseType("cash")
        t2 = ExpenseType.CASH
        assert t1 == t2

    def test_type_invalid_value_raises_error(self):
        """Test invalid type value raises error"""
        with pytest.raises(ValueError):
            ExpenseType("invalid_type")

    def test_type_name_to_value_mapping(self):
        """Test name to value mapping for types"""
        for exp_type in ExpenseType:
            retrieved = ExpenseType[exp_type.name]
            assert retrieved == exp_type


class TestEnumCaseInsensitivity:
    """Test enum case handling"""

    def test_category_value_is_lowercase(self):
        """Test category values are lowercase"""
        for category in ExpenseCategory:
            assert category.value == category.value.lower()

    def test_type_value_is_lowercase(self):
        """Test type values are lowercase"""
        for exp_type in ExpenseType:
            assert exp_type.value == exp_type.value.lower()

    def test_category_name_is_uppercase(self):
        """Test category names are uppercase"""
        for category in ExpenseCategory:
            assert category.name == category.name.upper()

    def test_type_name_is_uppercase(self):
        """Test type names are uppercase"""
        for exp_type in ExpenseType:
            assert exp_type.name == exp_type.name.upper()


class TestEnumDocumentation:
    """Test enum docstrings and metadata"""

    def test_category_enum_documented(self):
        """Test ExpenseCategory has documentation"""
        assert ExpenseCategory.__doc__ is not None

    def test_type_enum_documented(self):
        """Test ExpenseType has documentation"""
        assert ExpenseType.__doc__ is not None

    def test_all_categories_have_values(self):
        """Test we can access all 21 categories"""
        categories = [cat for cat in ExpenseCategory]
        assert len(categories) == 21

    def test_all_types_have_values(self):
        """Test we can access all 4 types"""
        types_list = [t for t in ExpenseType]
        assert len(types_list) == 4
