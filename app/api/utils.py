import logging
from typing import Any
from fastapi import Request
from app.core.config import templates, NAV_ITEMS
from app.db.database import supabase
from app.core.security import get_csrf_token, set_csrf_cookie
from app.crud.categories import fetch_categories
from app.crud.expenses import fetch_expenses
from app.crud.analytics import build_summary
from app.crud.income import fetch_income
from app.exceptions import DatabaseError

logger = logging.getLogger(__name__)

SETTINGS_CACHE: dict[str, dict[str, str] | None] = {}

def get_settings(user_id: str) -> dict[str, str]:
    defaults = {
        "currency_code": "NGN",
        "monthly_budget": "",
        "budget_alert": "80",
        "display_name": "New User",
    }
    try:
        response = supabase.table("settings").select("key, value").eq("user_id", user_id).execute()
        saved = {row["key"]: row["value"] for row in (response.data or [])}
        return {**defaults, **saved}
    except Exception as e:
        logger.warning(f"Failed to fetch settings for user {user_id}: {e}")
        return defaults

def enrich_settings(settings: dict[str, str]) -> dict[str, str]:
    currency_code = settings.get("currency_code", "NGN")
    settings["currency_symbol"] = "$" if currency_code == "USD" else "\u20a6"
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

def validate_redirect_url(url: str) -> str:
    if not url.startswith("/"):
        return "/dashboard"
    return url

def render_page(
    request: Request,
    template_name: str,
    active_page: str,
    user_id: str,
    **context: Any,
):
    try:
        resolved_settings = enrich_settings(context.get("settings") or get_settings(user_id))
        categories = fetch_categories(user_id)

        csrf_token = get_csrf_token(request)

        shared_context = {
            "request": request,
            "active_page": active_page,
            "nav_items": NAV_ITEMS,
            "settings": resolved_settings,
            "categories": categories,
            "csrf_token": csrf_token,
        }
        shared_context.update(context)
        shared_context["settings"] = resolved_settings

        if context.get("include_budget", True) and "summary" not in context:
            try:
                all_expenses = fetch_expenses(user_id)
                all_income = fetch_income(user_id)
                total_summary = build_summary(all_expenses, categories, all_income)
                shared_context["budget_status"] = get_budget_status(total_summary.get("total", 0.0), resolved_settings)
                shared_context["summary"] = total_summary
            except DatabaseError as e:
                logger.warning(f"Failed to compute budget status for user {user_id}: {e}")
                shared_context["budget_status"] = {"configured": False}
                shared_context["summary"] = {"total": 0, "total_income": 0, "balance": 0, "count": 0}

        response = templates.TemplateResponse(
            request=request,
            name=template_name,
            context=shared_context,
        )

        is_secure = request.url.scheme == "https"
        set_csrf_cookie(response, csrf_token, is_secure=is_secure)
        return response
    except DatabaseError:
        raise
    except Exception as e:
        logger.exception(f"Error rendering page {template_name}: {e}")
        raise
