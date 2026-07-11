from typing import TypedDict


class ExpenseData(TypedDict, total=False):
    id: str
    user_id: str
    title: str
    amount: float
    category: str
    expense_date: str
    notes: str
    receipt_image: str
    receipt_url: str | None


class IncomeData(TypedDict, total=False):
    id: str
    user_id: str
    title: str
    amount: float
    category: str
    income_date: str
    notes: str


class CategoryData(TypedDict, total=False):
    id: str
    user_id: str
    name: str
    color: str
    budget_limit: float


class RecurringData(TypedDict, total=False):
    id: str
    user_id: str
    title: str
    amount: float
    category: str
    frequency: str
    start_date: str
    next_occurrence: str
    notes: str


class CategoryProgress(TypedDict):
    name: str
    spent: float
    limit: float
    percentage: float
    is_over: bool
    color: str


class ChartData(TypedDict, total=False):
    labels: list[str]
    values: list[float]
    category_labels: list[str]
    category_values: list[float]
    category_colors: list[str]


class SummaryData(TypedDict, total=False):
    count: int
    total: float
    total_income: float
    balance: float
    categories: list[tuple[str, float]]
    category_progress: list[CategoryProgress]
    top_category: str
    chart_data: ChartData


class CategoryAnalytics(TypedDict):
    category: str
    amount: float
    percentage: float


class AnalyticsData(TypedDict):
    categories: list[CategoryAnalytics]
    insights: list[str]


class MonthlyReport(TypedDict):
    month: str
    spent: float
    income: float
    balance: float


class SettingsDict(TypedDict, total=False):
    currency_code: str
    monthly_budget: str
    budget_alert: str
    display_name: str
    currency_symbol: str


class BudgetStatus(TypedDict, total=False):
    configured: bool
    budget: float
    percentage: float
    is_alert: bool
    threshold: float
    remaining: float
