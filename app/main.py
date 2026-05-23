from __future__ import annotations

import csv
import sqlite3
from collections import defaultdict
from contextlib import asynccontextmanager
from io import StringIO
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "expenses.db"
NAV_ITEMS = [
    {"name": "Dashboard", "path": "/dashboard"},
    {"name": "Expenses", "path": "/expenses"},
    {"name": "Analytics", "path": "/analytics"},
    {"name": "Reports", "path": "/reports"},
    {"name": "AI Insights", "path": "/ai-insights"},
    {"name": "Settings", "path": "/settings"},
]


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                expense_date TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        connection.commit()



@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Expense Tracker", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def fetch_expenses() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, amount, category, expense_date, notes
            FROM expenses
            ORDER BY expense_date DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def filter_expenses(
    expenses: list[dict[str, Any]],
    date_from: str = "",
    date_to: str = "",
    category: str = "",
) -> list[dict[str, Any]]:
    filtered = expenses

    if date_from:
        filtered = [item for item in filtered if item["expense_date"] >= date_from]
    if date_to:
        filtered = [item for item in filtered if item["expense_date"] <= date_to]
    if category:
        filtered = [item for item in filtered if item["category"] == category]

    return filtered


def build_summary(expenses: list[dict[str, Any]]) -> dict[str, Any]:
    total = sum(item["amount"] for item in expenses)
    by_category: dict[str, float] = {}
    for item in expenses:
        by_category[item["category"]] = by_category.get(item["category"], 0.0) + item["amount"]

    top_categories = sorted(
        by_category.items(),
        key=lambda entry: entry[1],
        reverse=True,
    )

    top_category = top_categories[0][0] if top_categories else "None yet"

    return {
        "count": len(expenses),
        "total": total,
        "categories": top_categories,
        "top_category": top_category,
    }


def build_analytics(expenses: list[dict[str, Any]], summary: dict[str, Any]) -> list[dict[str, Any]]:
    total = summary["total"] or 0.0
    analytics = []

    for category, amount in summary["categories"]:
        percentage = 0.0 if total == 0 else (amount / total) * 100
        analytics.append(
            {
                "category": category,
                "amount": amount,
                "percentage": percentage,
            }
        )

    return analytics


def build_reports(expenses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    monthly_totals: dict[str, float] = defaultdict(float)

    for item in expenses:
        month_key = item["expense_date"][:7]
        monthly_totals[month_key] += item["amount"]

    report_rows = [
        {"month": month, "total": total}
        for month, total in sorted(monthly_totals.items(), reverse=True)
    ]
    return report_rows


def get_settings() -> dict[str, str]:
    defaults = {
        "currency_code": "NGN",
        "monthly_budget": "",
        "budget_alert": "80",
        "display_name": "Ademola",
    }

    with get_connection() as connection:
        rows = connection.execute("SELECT key, value FROM settings").fetchall()

    saved = {row["key"]: row["value"] for row in rows}
    return {**defaults, **saved}


def save_settings(values: dict[str, str]) -> None:
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            list(values.items()),
        )
        connection.commit()


def safe_next_url(next_url: str) -> str:
    return next_url if next_url.startswith("/") else "/expenses"


def get_budget_status(total_spent: float, settings: dict[str, str]) -> dict[str, Any]:
    budget_str = settings.get("monthly_budget", "")
    if not budget_str:
        return {"configured": False}
    try:
        budget = float(budget_str)
        if budget <= 0:
            return {"configured": False}

        threshold = float(settings.get("budget_alert", "80"))
        percentage = (total_spent / budget) * 100
        is_alert = percentage >= threshold
        return {
            "configured": True,
            "budget": budget,
            "percentage": percentage,
            "is_alert": is_alert,
            "threshold": threshold,
            "remaining": max(0.0, budget - total_spent),
        }
    except ValueError:
        return {"configured": False}


def render_page(
    request: Request,
    template_name: str,
    active_page: str,
    **context: Any,
):
    settings = get_settings()
    currency_code = settings.get("currency_code", "NGN")
    currency_symbol = "$" if currency_code == "USD" else "₦"
    settings["currency_symbol"] = currency_symbol

    shared_context = {
        "request": request,
        "active_page": active_page,
        "nav_items": NAV_ITEMS,
        "settings": settings,
    }
    shared_context.update(context)

    if "summary" in shared_context:
        summary = shared_context["summary"]
        shared_context["budget_status"] = get_budget_status(summary.get("total", 0.0), settings)

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=shared_context,
    )


@app.get("/")
def landing_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


@app.get("/dashboard")
def dashboard(request: Request):
    expenses = fetch_expenses()
    summary = build_summary(expenses)
    return render_page(
        request,
        "dashboard.html",
        "Dashboard",
        summary=summary,
        expenses=expenses[:5],
    )


@app.get("/ai-insights")
def ai_insights_page(request: Request):
    expenses = fetch_expenses()
    summary = build_summary(expenses)
    analytics = build_analytics(expenses, summary)
    return render_page(
        request,
        "ai_insights.html",
        "AI Insights",
        summary=summary,
        analytics=analytics,
        top_analytics=analytics[:3],
    )


@app.get("/expenses")
def expenses_page(request: Request):
    expenses = fetch_expenses()
    summary = build_summary(expenses)
    return render_page(
        request,
        "expenses.html",
        "Expenses",
        summary=summary,
        expenses=expenses,
    )


@app.get("/analytics")
def analytics_page(request: Request):
    expenses = fetch_expenses()
    summary = build_summary(expenses)
    analytics = build_analytics(expenses, summary)
    return render_page(
        request,
        "analytics.html",
        "Analytics",
        summary=summary,
        analytics=analytics,
    )


@app.get("/reports")
def reports_page(
    request: Request,
    date_from: str = "",
    date_to: str = "",
    category: str = "",
):
    all_expenses = fetch_expenses()
    expenses = filter_expenses(all_expenses, date_from=date_from, date_to=date_to, category=category)
    summary = build_summary(expenses)
    reports = build_reports(expenses)
    return render_page(
        request,
        "reports.html",
        "Reports",
        summary=summary,
        reports=reports,
        filters={
            "date_from": date_from,
            "date_to": date_to,
            "category": category,
        },
    )


@app.get("/settings")
def settings_page(request: Request, saved: int = 0):
    summary = build_summary(fetch_expenses())
    settings = get_settings()
    return render_page(
        request,
        "settings.html",
        "Settings",
        summary=summary,
        settings=settings,
        saved=bool(saved),
    )


@app.get("/reports/export")
def export_reports(
    date_from: str = "",
    date_to: str = "",
    category: str = "",
):
    all_expenses = fetch_expenses()
    expenses = filter_expenses(all_expenses, date_from=date_from, date_to=date_to, category=category)
    reports = build_reports(expenses)

    settings = get_settings()
    currency_code = settings.get("currency_code", "NGN").lower()

    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(["month", f"total_spent_{currency_code}"])
    for row in reports:
        writer.writerow([row["month"], f'{row["total"]:.2f}'])

    stream.seek(0)
    headers = {"Content-Disposition": "attachment; filename=expense_report.csv"}
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers=headers)


@app.post("/expenses")
def create_expense(
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    expense_date: str = Form(...),
    notes: str = Form(""),
    next_url: str = Form("/expenses"),
):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO expenses (title, amount, category, expense_date, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title.strip(), amount, category.strip(), expense_date, notes.strip()),
        )
        connection.commit()

    return RedirectResponse(url=safe_next_url(next_url), status_code=303)


@app.post("/expenses/{expense_id}/delete")
def delete_expense(
    expense_id: int,
    next_url: str = Form("/expenses"),
):
    with get_connection() as connection:
        connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        connection.commit()

    return RedirectResponse(url=safe_next_url(next_url), status_code=303)


@app.post("/settings")
def update_settings(
    currency_code: str = Form("NGN"),
    monthly_budget: str = Form(""),
    budget_alert: str = Form("80"),
    display_name: str = Form(""),
):
    save_settings(
        {
            "currency_code": currency_code.strip().upper() or "NGN",
            "monthly_budget": monthly_budget.strip(),
            "budget_alert": budget_alert.strip() or "80",
            "display_name": display_name.strip() or "Ademola",
        }
    )
    return RedirectResponse(url="/settings?saved=1", status_code=303)
