from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.api.utils import render_page
from app.db.database import supabase
from app.crud.analytics import build_summary
from app.crud.expenses import fetch_expenses
from app.crud.income import fetch_income
from app.exceptions import DatabaseError
from app.core.security import require_csrf
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/settings")
def settings_page(request: Request, saved: int = 0, cleared: int = 0):
    try:
        user_id = require_user(request)
        summary = build_summary(fetch_expenses(user_id), income=fetch_income(user_id))
        
        return render_page(
            request,
            "settings.html",
            "Settings",
            user_id,
            summary=summary,
            saved=bool(saved),
            cleared=bool(cleared),
        )
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/settings")
def update_settings(
    request: Request,
    currency_code: str = Form("NGN"),
    monthly_budget: str = Form(""),
    budget_alert: str = Form("80"),
    display_name: str = Form(""),
):
    try:
        user_id = require_user(request)
        
        try:
            response = supabase.table("users").select("username").eq("id", user_id).execute()
        except Exception as e:
            raise DatabaseError("Failed to fetch user data", original_exception=e)
            
        username = response.data[0]["username"] if response.data else "User"
            
        values = {
            "currency_code": currency_code.strip().upper() or "NGN",
            "monthly_budget": monthly_budget.strip(),
            "budget_alert": budget_alert.strip() or "80",
            "display_name": display_name.strip() or username,
        }
        
        logger.info(f"Updating settings for user {user_id}: {values}")
        for key, value in values.items():
            try:
                supabase.table("settings").upsert({"user_id": user_id, "key": key, "value": value}).execute()
            except Exception as e:
                raise DatabaseError(f"Failed to update setting: {key}", original_exception=e)
            
        return RedirectResponse(url="/settings?saved=1", status_code=303)
    except DatabaseError as de:
        logger.error(f"Database error updating settings: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error updating settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")

@router.post("/settings/delete-account")
def delete_account(
    request: Request,
    csrf_token: str = Form(...),
):
    try:
        user_id = require_user(request)
        require_csrf(request, csrf_token)
        
        from app.crud.settings import delete_user_account
        delete_user_account(user_id)
        
        response = RedirectResponse(url="/register?deleted=1", status_code=303)
        response.delete_cookie("supabase_auth_token")
        return response
    except DatabaseError as de:
        logger.error(f"Database error deleting account: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error deleting account: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account")

@router.post("/categories/{category_id}/budget")
def update_cat_budget(
    request: Request,
    category_id: str,
    budget_limit: float = Form(...),
    csrf_token: str = Form(...),
):
    try:
        user_id = require_user(request)
        require_csrf(request, csrf_token)
        
        from app.crud.categories import update_category_budget
        update_category_budget(user_id, category_id, budget_limit)
        
        return RedirectResponse(url="/settings?saved=1", status_code=303)
    except Exception as e:
        logger.error(f"Error updating category budget: {e}")
        raise HTTPException(status_code=500, detail="Failed to update category budget")
