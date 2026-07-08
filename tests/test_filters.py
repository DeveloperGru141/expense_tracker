from app.crud.expenses import filter_expenses
from app.crud.income import filter_income
from app.schemas.models import ExpenseData, IncomeData


class TestFilterExpenses:
    def setup_method(self):
        self.expenses: list[ExpenseData] = [
            ExpenseData(title="A", amount=10, category="Food", expense_date="2026-07-01", notes=""),
            ExpenseData(title="B", amount=20, category="Transport", expense_date="2026-07-15", notes=""),
            ExpenseData(title="C", amount=30, category="Food", expense_date="2026-08-01", notes=""),
        ]

    def test_no_filter(self):
        result = filter_expenses(self.expenses)
        assert len(result) == 3

    def test_date_from(self):
        result = filter_expenses(self.expenses, date_from="2026-07-15")
        assert len(result) == 2
        assert all(e["expense_date"] >= "2026-07-15" for e in result)

    def test_date_to(self):
        result = filter_expenses(self.expenses, date_to="2026-07-15")
        assert len(result) == 2
        assert all(e["expense_date"] <= "2026-07-15" for e in result)

    def test_date_range(self):
        result = filter_expenses(self.expenses, date_from="2026-07-01", date_to="2026-07-31")
        assert len(result) == 2

    def test_category(self):
        result = filter_expenses(self.expenses, category="Food")
        assert len(result) == 2
        assert all(e["category"] == "Food" for e in result)

    def test_all_filters(self):
        result = filter_expenses(self.expenses, date_from="2026-07-01", date_to="2026-07-31", category="Food")
        assert len(result) == 1
        assert result[0]["title"] == "A"

    def test_empty_list(self):
        assert filter_expenses([]) == []


class TestFilterIncome:
    def setup_method(self):
        self.income: list[IncomeData] = [
            IncomeData(title="Salary", amount=5000, category="Work", income_date="2026-07-01", notes=""),
            IncomeData(title="Freelance", amount=500, category="Side", income_date="2026-07-15", notes=""),
        ]

    def test_no_filter(self):
        assert len(filter_income(self.income)) == 2

    def test_category_filter(self):
        result = filter_income(self.income, category="Work")
        assert len(result) == 1
        assert result[0]["title"] == "Salary"

    def test_date_from(self):
        result = filter_income(self.income, date_from="2026-07-15")
        assert len(result) == 1

    def test_date_to(self):
        result = filter_income(self.income, date_to="2026-07-01")
        assert len(result) == 1
