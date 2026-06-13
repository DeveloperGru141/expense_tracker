from datetime import date
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.api.utils import render_page
from app.core.security import require_csrf
from app.crud.expenses import fetch_expenses
from app.crud.analytics import build_summary
from app.crud.recurring import process_recurring_expenses, fetch_recurring_expenses, fetch_recurring_income
from app.db.database import supabase
from app.exceptions import DatabaseError
from app.core.limiter import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/recurring")
def recurring_page(request: Request):
    try:
        user_id = require_user(request)
        process_recurring_expenses(user_id)
        
        recurrings = fetch_recurring_expenses(user_id)
        recurring_incomes = fetch_recurring_income(user_id)
        summary = build_summary(fetch_expenses(user_id))
        
        return render_page(
            request,
            "recurring.html",
            "Recurring",
            user_id,
            recurrings=recurrings,
            recurring_incomes=recurring_incomes,
            summary=summary,
        )
    except DatabaseError as de:
        logger.error(f"Database error loading recurring page: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error loading recurring page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/recurring")
@limiter.limit("10/minute")
def create_recurring(
    request: Request,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    frequency: str = Form(...),
    start_date: str = Form(...),
    notes: str = Form(""),
    type: str = Form("expense"),
    csrf_token: str = Form(...),
):
    try:
        user_id = require_user(request)
        require_csrf(request, csrf_token)
        
        if amount <= 0:
            raise HTTPException(status_code=422, detail="Amount must be positive")
        
        valid_frequencies = ["daily", "weekly", "monthly", "yearly"]
        if frequency not in valid_frequencies:
            raise HTTPException(status_code=422, detail=f"Invalid frequency. Must be one of: {', '.join(valid_frequencies)}")
        
        try:
            date.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format")
        
        table = "recurring_expenses" if type == "expense" else "recurring_income"
        recurring_data = {
            "user_id": user_id,
            "title": title.strip(),
            "amount": amount,
            "category": category.strip(),
            "frequency": frequency,
            "start_date": start_date,
            "next_occurrence": start_date,
            "notes": notes.strip()
        }
        
        logger.info(f"Creating recurring {type} for user {user_id}: {title}")
        supabase.table(table).insert(recurring_data).execute()
            
        return RedirectResponse(url="/recurring", status_code=303)
    except HTTPException:
        raise
    except DatabaseError as de:
        logger.error(f"Database error creating recurring transaction: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error creating recurring transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to create recurring transaction")

@router.post("/recurring/{recurring_id}/delete")
@limiter.limit("10/minute")
def delete_recurring(
    request: Request, 
    recurring_id: str, 
    type: str = Form("expense"), 
    csrf_token: str = Form(...),
):
    try:
        user_id = require_user(request)
        require_csrf(request, csrf_token)
        
        table = "recurring_expenses" if type == "expense" else "recurring_income"
        try:
            supabase.table(table).delete().eq("id", recurring_id).eq("user_id", user_id).execute()
        except Exception as e:
            raise DatabaseError(f"Failed to delete recurring {type}", original_exception=e)
            
        return RedirectResponse(url="/recurring", status_code=303)
    except DatabaseError as de:
        logger.error(f"Database error deleting recurring transaction: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error deleting recurring transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete recurring transaction")
