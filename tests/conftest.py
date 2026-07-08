import pytest
from app.schemas.models import ExpenseData, IncomeData, CategoryData

SAMPLE_EXPENSES: list[ExpenseData] = [
    ExpenseData(title="Groceries", amount=150.00, category="Food", expense_date="2026-07-01", notes="Weekly shop"),
    ExpenseData(title="Gas", amount=80.00, category="Transport", expense_date="2026-07-02", notes=""),
    ExpenseData(title="Dinner", amount=45.00, category="Food", expense_date="2026-06-28", notes="Restaurant"),
    ExpenseData(title="Netflix", amount=15.99, category="Entertainment", expense_date="2026-07-05", notes="Monthly sub"),
    ExpenseData(title="Gym", amount=50.00, category="Health", expense_date="2026-07-01", notes="Monthly"),
]

SAMPLE_INCOME: list[IncomeData] = [
    IncomeData(title="Salary", amount=5000.00, category="Work", income_date="2026-07-01", notes="Monthly"),
    IncomeData(title="Freelance", amount=500.00, category="Side", income_date="2026-07-10", notes="Project"),
]

SAMPLE_CATEGORIES: list[CategoryData] = [
    CategoryData(id="1", user_id="u1", name="Food", color="#ef4444", budget_limit=500.0),
    CategoryData(id="2", user_id="u1", name="Transport", color="#3b82f6", budget_limit=200.0),
    CategoryData(id="3", user_id="u1", name="Entertainment", color="#f59e0b", budget_limit=100.0),
    CategoryData(id="4", user_id="u1", name="Health", color="#10b981", budget_limit=300.0),
]


@pytest.fixture
def sample_expenses():
    return SAMPLE_EXPENSES.copy()


@pytest.fixture
def sample_income():
    return SAMPLE_INCOME.copy()


@pytest.fixture
def sample_categories():
    return SAMPLE_CATEGORIES.copy()
