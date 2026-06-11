from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.api.utils import render_page
from app.db.database import supabase

router = APIRouter()

@router.get("/settings")
def settings_page(request: Request, saved: int = 0):
    user_id = require_user(request)
    # Fetch income, expenses, etc. through CRUD
    from app.crud.expenses import fetch_expenses
    from app.crud.income import fetch_income
    summary = build_summary(fetch_expenses(user_id), income=fetch_income(user_id))
    
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
):
    user_id = require_user(request)
    
    response = supabase.table("users").select("username").eq("id", user_id).execute()
    username = response.data[0]["username"] if response.data else "User"
        
    values = {
        "currency_code": currency_code.strip().upper() or "NGN",
        "monthly_budget": monthly_budget.strip(),
        "budget_alert": budget_alert.strip() or "80",
        "display_name": display_name.strip() or username,
    }
    
    for key, value in values.items():
        supabase.table("settings").upsert({"user_id": user_id, "key": key, "value": value}).execute()
        
    return RedirectResponse(url="/settings?saved=1", status_code=303)

@router.post("/categories/{category_id}/budget")
def update_cat_budget(
    request: Request,
    category_id: str, # Supabase uses UUIDs
    budget_limit: float = Form(...),
):
    user_id = require_user(request)
    
    from app.crud.categories import update_category_budget
    update_category_budget(user_id, category_id, budget_limit)
    
    return RedirectResponse(url="/settings?saved=1", status_code=303)
