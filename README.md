# Finito App Backend

Expense management system with clean architecture in Python.

## 📋 Description

Finito App is a backend application for controlling and organizing expenses in groups. It allows creating, viewing, updating, and deleting expenses with support for different categories and payment methods.

## 🏗️ Architecture

The project follows a layered architecture (Clean Architecture):

```
app/
├── api.py                          # FastAPI application configuration
├── controllers/                    # Controllers (orchestration)
│   └── expense_controller.py
├── routes/                         # HTTP routes definition
│   └── expense_routes.py
├── use_cases/                      # Use cases (business logic)
│   └── expense/
│       ├── create_expense.py
│       ├── get_all_expenses.py
│       ├── get_expense_by_id.py
│       ├── update_expense.py
│       ├── delete_expense.py
│       └── get_amounts_and_types.py
├── domain/                         # Entities and interfaces
│   ├── entities/
│   │   ├── base_entity.py
│   │   └── expense_entity.py
│   ├── enums/
│   │   ├── expense_category_enum.py
│   │   └── expense_type_enum.py
│   ├── interfaces/
│   │   ├── repository.py
│   │   ├── use_case.py
│   │   └── expense_repository_interface.py
│   └── dtos/
│       └── expense_dtos.py
├── infrastructure/                 # Technical implementations
│   ├── database.py
│   ├── logger.py
│   ├── settings.py
│   ├── dependencies.py
│   └── repositories/
│       └── expense_repository.py
└── models/                         # Pydantic schemas
    └── expense_schema.py
```

## 🚀 Getting Started

### Prerequisites

- Python 3.14+
- MongoDB (local or remote)
- pip (package manager)

### Installation

1. **Clone the repository:**

```bash
git clone <repository-url>
cd Finito_app_backend
```

2. **Create a virtual environment:**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

Create a `.env` file in the project root:

```bash
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=finito_db
LOG_LEVEL=INFO
```

### Running the Application

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

Interactive documentation (Swagger): `http://localhost:8000/docs`

## 🧪 Tests

### Run all tests:

```bash
python -m pytest tests/app -v
```

### Run tests with coverage:

```bash
python -m pytest tests/app --cov=app --cov-report=html
```

### Run specific tests:

```bash
python -m pytest tests/app/domain/ -v
python -m pytest tests/app/controllers/ -v
```

### Current test status:

- ✅ **208 tests passing**
- 📊 Coverage: 57%

## 📦 Main Dependencies

- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **Motor** - Async MongoDB driver
- **Python-dotenv** - Environment variables management
- **Pytest** - Testing framework
- **Pytest-cov** - Coverage plugin

## 🔌 Main Endpoints

### Expenses

| Method   | Route                                        | Description         |
| -------- | -------------------------------------------- | ------------------- |
| `POST`   | `/api/expenses`                              | Create new expense  |
| `GET`    | `/api/expenses`                              | List all expenses   |
| `GET`    | `/api/expenses/{id}`                         | Get expense by ID   |
| `PUT`    | `/api/expenses/{id}`                         | Update expense      |
| `DELETE` | `/api/expenses/{id}`                         | Delete expense      |
| `GET`    | `/api/expenses/amounts-and-types/{group_id}` | Get amounts by type |

## 📊 Data Structure

### Expense

```python
{
  "id": "507f1f77bcf86cd799439011",
  "group_id": "507f1f77bcf86cd799439012",
  "amount_cents": 2500,  # Amount in cents
  "category": "food",
  "type_expense": "credit_card",
  "spent_by": "John Doe",
  "date": "2026-02-10T12:00:00Z",
  "note": "Lunch at restaurant",
  "is_deleted": false,
  "created_at": "2026-02-10T12:00:00Z",
  "updated_at": "2026-02-10T12:00:00Z"
}
```

### Expense Categories

- `transportation` - Transportation
- `entertainment` - Entertainment
- `utilities` - Utilities
- `healthcare` - Healthcare
- `education` - Education
- `shopping` - Shopping
- `subscriptions` - Subscriptions
- `personal_care` - Personal care
- `home` - Home
- `bills` - Bills
- `work` - Work
- `gifts` - Gifts
- `insurance` - Insurance
- `savings` - Savings
- `investments` - Investments
- `pet` - Pet
- `groceries` - Groceries
- `restaurants` - Restaurants
- `gas` - Gas
- `car` - Car
- `other` - Other

### Payment Methods

- `cash` - Cash
- `credit_card` - Credit card
- `debit_card` - Debit card
- `pix_transfer` - Pix transfer
- `bank_transfer` - Bank transfer
- `check` - Check
- `other` - Other

## 🔧 Configuration

Application configuration is centralized in `app/infrastructure/settings.py`:

```python
MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DB_NAME = "finito_db"
LOG_LEVEL = "INFO"
```

## 🐳 Docker

The application can be run in a Docker container:

```bash
# Build the image
docker build -t finito-app-backend .

# Run container
docker run -p 8000:8000 --env-file .env finito-app-backend
```

With Docker Compose:

```bash
docker-compose up -d
```

## 📝 Code Standards

### Naming Conventions

- Classes: `PascalCase` (e.g., `ExpenseController`)
- Functions/methods: `snake_case` (e.g., `create_expense`)
- Constants: `UPPERCASE` (e.g., `MONGODB_URL`)

### Test Structure

```python
class TestClassName:
    """Test description"""

    def test_something(self):
        """Test case description"""
        # Arrange
        # Act
        # Assert
```

## 🔐 Security

- Input validation with Pydantic
- NoSQL injection protection with Motor
- Sensitive variables in `.env` (never commit)

## 📚 Additional Documentation

Automatic documentation available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
2. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
3. Push to the branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Felipe**

## 📞 Support

For questions and suggestions, open an issue in the repository.

---

**Last updated:** February 10, 2026
