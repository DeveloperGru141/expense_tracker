from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.api.utils import render_page
from app.core.security import require_csrf
from app.crud.expenses import fetch_expenses
from app.crud.analytics import build_summary
from app.crud.recurring import process_recurring_expenses, fetch_recurring_expenses, fetch_recurring_income
from app.db.database import supabase
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
    except Exception as e:
        logger.error(f"Error loading recurring page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/recurring")
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
        logger.info(f"Adding recurring transaction for user {user_id}: {recurring_data}")
        supabase.table(table).insert(recurring_data).execute()
        return RedirectResponse(url="/recurring", status_code=303)
    except Exception as e:
        logger.exception(f"Error creating recurring transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to create recurring transaction")

@router.post("/recurring/{recurring_id}/delete")
def delete_recurring(request: Request, recurring_id: str, type: str = Form("expense"), csrf_token: str = Form(...)):
    try:
        user_id = require_user(request)
        require_csrf(request, csrf_token)
        table = "recurring_expenses" if type == "expense" else "recurring_income"
        supabase.table(table).delete().eq("id", recurring_id).eq("user_id", user_id).execute()
        return RedirectResponse(url="/recurring", status_code=303)
    except Exception as e:
        logger.error(f"Error deleting recurring transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete recurring transaction")
