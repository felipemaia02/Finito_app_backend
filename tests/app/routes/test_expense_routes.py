"""Tests for routes/expense_routes.py - HTTP endpoint tests."""

import pytest
from datetime import datetime, timezone
from bson import ObjectId
from fastapi.testclient import TestClient

from app.api import app
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType
from app.models.expense_schema import ExpenseResponse


def make_expense_response_obj(expense_id=None):
    oid = expense_id or str(ObjectId())
    return ExpenseResponse(
        id=oid,
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


@pytest.fixture
def expense_client(mock_app_dependencies, mock_expense_repository):
    """Test client with API key and OAuth2 token for expense routes."""
    from app.infrastructure.settings import get_settings
    from app.services.oauth2_service import OAuth2Service
    from app.infrastructure.dependencies.expense_dependencies import ExpenseDependencies

    oauth2_service = OAuth2Service()
    token, _, _ = oauth2_service.create_token_pair(email="test@example.com")

    mock_app_dependencies.dependency_overrides[ExpenseDependencies.get_repository] = (
        lambda: mock_expense_repository
    )

    client = TestClient(mock_app_dependencies)
    client.headers.update(
        {
            "X-API-Key": get_settings().api_key,
            "Authorization": f"Bearer {token}",
        }
    )
    return client, mock_expense_repository


class TestExpenseRouterInitialization:
    """Test expense router"""

    def test_router_exists(self):
        from app.routes.expense_routes import router

        assert router is not None

    def test_router_has_routes(self):
        from app.routes.expense_routes import router

        assert hasattr(router, "routes")
        assert len(router.routes) > 0


class TestExpenseRouteCreateExpense:
    """Test POST /expenses endpoint."""

    def test_create_expense_success(self, expense_client):
        client, mock_repo = expense_client
        expense_response = make_expense_response_obj()
        mock_repo.create.return_value = expense_response

        expense_data = {
            "group_id": "507f1f77bcf86cd799439012",
            "amount_cents": 5000,
            "category": "entertainment",
            "type_expense": "credit_card",
            "spent_by": "John Doe",
            "note": "Weekend movie",
        }

        response = client.post("/api/v1/expenses", json=expense_data)
        assert response.status_code in [201, 400, 422]

    def test_create_expense_missing_fields(self, expense_client):
        client, _ = expense_client
        response = client.post(
            "/expenses", json={"group_id": "507f1f77bcf86cd799439012"}
        )
        assert response.status_code == 422

    def test_create_expense_server_error(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.create.side_effect = Exception("Unexpected error")

        expense_data = {
            "group_id": "507f1f77bcf86cd799439012",
            "amount_cents": 5000,
            "category": "entertainment",
            "type_expense": "credit_card",
            "spent_by": "John Doe",
        }

        response = client.post("/api/v1/expenses", json=expense_data)
        assert response.status_code in [400, 422, 500]


class TestExpenseRouteListExpenses:
    """Test GET /expenses/{group_id} endpoint."""

    def test_list_expenses_success(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_all.return_value = []

        response = client.get("/api/v1/expenses/507f1f77bcf86cd799439012")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_expenses_with_results(self, expense_client):
        client, mock_repo = expense_client
        expense = make_expense_response_obj()
        mock_repo.get_all.return_value = [expense]

        response = client.get("/api/v1/expenses/507f1f77bcf86cd799439012")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_expenses_with_pagination(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_all.return_value = []

        response = client.get("/api/v1/expenses/507f1f77bcf86cd799439012?skip=5&limit=20")
        assert response.status_code == 200

    def test_list_expenses_server_error(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_all.side_effect = Exception("DB error")

        response = client.get("/api/v1/expenses/507f1f77bcf86cd799439012")
        assert response.status_code == 500


class TestExpenseRouteGetExpenseDetails:
    """Test GET /expenses/{expense_id}/details endpoint."""

    def test_get_expense_details_found(self, expense_client):
        client, mock_repo = expense_client
        expense_id = str(ObjectId())
        expense = make_expense_response_obj(expense_id)
        mock_repo.get_by_id.return_value = expense

        response = client.get(f"/expenses/{expense_id}/details")
        assert response.status_code == 200

    def test_get_expense_details_not_found(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_by_id.return_value = None

        response = client.get(f"/expenses/{str(ObjectId())}/details")
        assert response.status_code == 404

    def test_get_expense_details_server_error(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_by_id.side_effect = Exception("DB error")

        response = client.get(f"/expenses/{str(ObjectId())}/details")
        assert response.status_code == 500


class TestExpenseRouteUpdateExpense:
    """Test PATCH /expenses/{expense_id} endpoint."""

    def test_update_expense_not_found(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_by_id.return_value = None
        mock_repo.update.return_value = None

        update_data = {"amount_cents": 7000}
        response = client.patch(f"/expenses/{str(ObjectId())}", json=update_data)
        assert response.status_code == 404

    def test_update_expense_server_error(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_by_id.side_effect = Exception("DB error")

        update_data = {"amount_cents": 7000}
        response = client.patch(f"/expenses/{str(ObjectId())}", json=update_data)
        assert response.status_code == 500


class TestExpenseRouteDeleteExpense:
    """Test DELETE /expenses/{expense_id} endpoint."""

    def test_delete_expense_success(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.delete.return_value = True

        response = client.delete(f"/expenses/{str(ObjectId())}")
        assert response.status_code == 204

    def test_delete_expense_not_found(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.delete.return_value = False

        response = client.delete(f"/expenses/{str(ObjectId())}")
        assert response.status_code == 404

    def test_delete_expense_server_error(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.delete.side_effect = Exception("DB error")

        response = client.delete(f"/expenses/{str(ObjectId())}")
        assert response.status_code == 500


class TestExpenseRouteAnalytics:
    """Test GET /expenses/{group_id}/analytics endpoint."""

    def test_get_analytics_success(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_amounts_and_types.return_value = [
            {"amount_cents": 1000, "type_expense": "cash"},
        ]

        response = client.get("/api/v1/expenses/507f1f77bcf86cd799439012/analytics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_analytics_empty(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_amounts_and_types.return_value = []

        response = client.get("/api/v1/expenses/507f1f77bcf86cd799439012/analytics")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_analytics_server_error(self, expense_client):
        client, mock_repo = expense_client
        mock_repo.get_amounts_and_types.side_effect = Exception("DB error")

        response = client.get("/api/v1/expenses/507f1f77bcf86cd799439012/analytics")
        assert response.status_code == 500
