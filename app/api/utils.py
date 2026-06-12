from typing import Any
from fastapi import Request
from app.core.config import templates, NAV_ITEMS
from app.db.database import supabase
from app.core.security import get_csrf_token
from app.crud.categories import fetch_categories
from app.crud.expenses import fetch_expenses
from app.crud.analytics import build_summary

def get_settings(user_id: str) -> dict[str, str]:
    defaults = {
        "currency_code": "NGN",
        "monthly_budget": "",
        "budget_alert": "80",
        "display_name": "New User",
    }
    response = supabase.table("settings").select("key, value").eq("user_id", user_id).execute()
    saved = {row["key"]: row["value"] for row in response.data}
    return {**defaults, **saved}

def enrich_settings(settings: dict[str, str]) -> dict[str, str]:
    currency_code = settings.get("currency_code", "NGN")
    settings["currency_symbol"] = "$" if currency_code == "USD" else "₦"
    return settings

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
        return {
            "configured": True,
            "budget": budget,
            "percentage": percentage,
            "is_alert": percentage >= threshold,
            "threshold": threshold,
            "remaining": max(0.0, budget - total_spent),
        }
    except ValueError:
        return {"configured": False}

def render_page(
    request: Request,
    template_name: str,
    active_page: str,
    user_id: str,
    **context: Any,
):
    resolved_settings = enrich_settings(context.get("settings") or get_settings(user_id))
    categories = fetch_categories(user_id)
    
    shared_context = {
        "request": request,
        "active_page": active_page,
        "nav_items": NAV_ITEMS,
        "settings": resolved_settings,
        "categories": categories,
        "csrf_token": get_csrf_token(request),
    }
    shared_context.update(context)
    shared_context["settings"] = resolved_settings
    
    # Global budget status based on ALL expenses for the user
    if context.get("include_budget", True):
        from app.crud.income import fetch_income
        all_expenses = fetch_expenses(user_id)
        all_income = fetch_income(user_id)
        total_summary = build_summary(all_expenses, categories, all_income)
        shared_context["budget_status"] = get_budget_status(total_summary.get("total", 0.0), resolved_settings)
        if "summary" not in shared_context:
            shared_context["summary"] = total_summary
        
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=shared_context,
    )
