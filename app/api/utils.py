from typing import Any
from fastapi import Request
from app.core.config import templates, NAV_ITEMS
from app.core.security import get_csrf_token, set_csrf_cookie
from app.db.database import get_connection

def get_settings(user_id: int) -> dict[str, str]:
    defaults = {
        "currency_code": "NGN",
        "monthly_budget": "",
        "budget_alert": "80",
        "display_name": "New User",
    }
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT key, value FROM settings WHERE user_id = ?", (user_id,)
        ).fetchall()
    saved = {row["key"]: row["value"] for row in rows}
    return {**defaults, **saved}

def enrich_settings(settings: dict[str, str]) -> dict[str, str]:
    currency_code = settings.get("currency_code", "NGN")
    settings["currency_symbol"] = "$" if currency_code == "USD" else "\u20A6"
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
    user_id: int,
    **context: Any,
):
    from app.crud.categories import fetch_categories # Avoid circular import
    
    resolved_settings = enrich_settings(context.get("settings") or get_settings(user_id))
    csrf_token = get_csrf_token(request)
    categories = fetch_categories(user_id)
    
    shared_context = {
        "request": request,
        "active_page": active_page,
        "nav_items": NAV_ITEMS,
        "settings": resolved_settings,
        "csrf_token": csrf_token,
        "categories": categories,
    }
    shared_context.update(context)
    shared_context["settings"] = resolved_settings
    
    if "summary" in shared_context:
        from app.crud.expenses import fetch_expenses
        all_expenses = fetch_expenses(user_id)
        from app.crud.analytics import build_summary
        shared_context["summary"] = build_summary(all_expenses, categories)
        shared_context["budget_status"] = get_budget_status(shared_context["summary"].get("total", 0.0), resolved_settings)
        
    response = templates.TemplateResponse(
        request=request,
        name=template_name,
        context=shared_context,
    )
    set_csrf_cookie(response, csrf_token)
    return response
