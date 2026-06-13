import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi.templating import Jinja2Templates

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "expenses.db"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET environment variable is required")
AUTH_COOKIE = "expense_tracker_auth"
CSRF_COOKIE = "expense_tracker_csrf"

NAV_ITEMS = [
    {"name": "Dashboard", "path": "/dashboard", "icon": "◉"},
    {"name": "Expenses", "path": "/expenses", "icon": "⊘"},
    {"name": "Income", "path": "/income", "icon": "⊕"},
    {"name": "Recurring", "path": "/recurring", "icon": "⟳"},
    {"name": "Analytics", "path": "/analytics", "icon": "◈"},
    {"name": "Reports", "path": "/reports", "icon": "▤"},
    {"name": "AI Insights", "path": "/ai-insights", "icon": "✦"},
    {"name": "Settings", "path": "/settings", "icon": "⚙"},
]
