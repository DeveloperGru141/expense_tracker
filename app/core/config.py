import os
from pathlib import Path

from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "expenses.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

SESSION_SECRET = os.getenv("SESSION_SECRET", "local-dev-secret-change-me")
AUTH_COOKIE = "expense_tracker_auth"
CSRF_COOKIE = "expense_tracker_csrf"

NAV_ITEMS = [
    {"name": "Dashboard", "path": "/dashboard"},
    {"name": "Expenses", "path": "/expenses"},
    {"name": "Income", "path": "/income"},
    {"name": "Recurring", "path": "/recurring"},
    {"name": "Analytics", "path": "/analytics"},
    {"name": "Reports", "path": "/reports"},
    {"name": "AI Insights", "path": "/ai-insights"},
    {"name": "Settings", "path": "/settings"},
]
