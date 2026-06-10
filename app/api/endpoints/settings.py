from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.api.utils import render_page, get_settings
from app.core.security import require_csrf
from app.crud.expenses import fetch_expenses
from app.crud.analytics import build_summary
from app.db.database import get_connection

router = APIRouter()

@router.get("/settings")
def settings_page(request: Request, saved: int = 0):
    user_id = require_user(request)
    summary = build_summary(fetch_expenses(user_id))
    return render_page(
        request,
        "settings.html",
        "Settings",
        user_id,
        summary=summary,
        saved=bool(saved),
    )

@router.post("/settings")
def update_settings(
    request: Request,
    currency_code: str = Form("NGN"),
    monthly_budget: str = Form(""),
    budget_alert: str = Form("80"),
    display_name: str = Form(""),
    csrf_token: str = Form(...),
):
    user_id = require_user(request)
    require_csrf(request, csrf_token)
    
    with get_connection() as connection:
        user = connection.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
        default_name = user["username"] if user else "User"
        
    values = {
        "currency_code": currency_code.strip().upper() or "NGN",
        "monthly_budget": monthly_budget.strip(),
        "budget_alert": budget_alert.strip() or "80",
        "display_name": display_name.strip() or default_name,
    }
    
    from app.api.utils import get_settings # avoid potential issues
    # I'll just use the save_settings logic here or move it to crud
    with get_connection() as connection:
        for key, value in values.items():
            connection.execute(
                """
                INSERT INTO settings (user_id, key, value)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, key) DO UPDATE SET value = excluded.value
                """,
                (user_id, key, value),
            )
        connection.commit()
        
    return RedirectResponse(url="/settings?saved=1", status_code=303)

@router.post("/categories/{category_id}/budget")
def update_cat_budget(
    request: Request,
    category_id: int,
    budget_limit: float = Form(...),
    csrf_token: str = Form(...),
):
    user_id = require_user(request)
    require_csrf(request, csrf_token)
    
    from app.crud.categories import update_category_budget
    update_category_budget(user_id, category_id, budget_limit)
    
    return RedirectResponse(url="/settings?saved=1", status_code=303)
