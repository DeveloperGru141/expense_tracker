from datetime import date
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.core.security import require_csrf
from app.crud.income import fetch_income, create_income, delete_income
from app.crud.recurring import process_recurring_expenses
from app.api.utils import render_page
from app.exceptions import AuthError, DatabaseError
from app.core.limiter import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_TITLE_LENGTH = 200
MAX_NOTES_LENGTH = 1000
MAX_SEARCH_LENGTH = 100

# Show the income listing page with optional search.
@router.get("/income")
@limiter.limit("30/minute")
def income_page(request: Request, q: str = ""):
    try:
        user_id = require_user(request)
        q = q[:MAX_SEARCH_LENGTH] if q else ""
        process_recurring_expenses(user_id)
        income_list = fetch_income(user_id, search=q)

        return render_page(
            request,
            "income.html",
            "Income",
            user_id,
            income_list=income_list,
            search_query=q,
        )
    except (AuthError, HTTPException):
        raise
    except DatabaseError as de:
        logger.error(f"Database error loading income: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.error(f"Unexpected error loading income page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Handle adding a new income entry.
@router.post("/income")
@limiter.limit("10/minute")
def add_income(
    request: Request,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    income_date: str = Form(...),
    notes: str = Form(""),
    csrf_token: str = Form(...),
):
    try:
        user_id = require_user(request)
        require_csrf(request, csrf_token)

        title = title.strip()[:MAX_TITLE_LENGTH]
        notes = notes.strip()[:MAX_NOTES_LENGTH]
        category = category.strip()[:100]

        if not title:
            raise HTTPException(status_code=422, detail="Title is required")
        if amount <= 0:
            raise HTTPException(status_code=422, detail="Amount must be positive")
        if not category:
            raise HTTPException(status_code=422, detail="Category is required")

        try:
            date.fromisoformat(income_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format")

        income_data = {
            "title": title,
            "amount": amount,
            "category": category,
            "income_date": income_date,
            "notes": notes,
        }
        logger.info(f"Adding income for user {user_id}: {title}")
        create_income(user_id, income_data)

        return RedirectResponse(url="/income", status_code=303)
    except (AuthError, HTTPException):
        raise
    except Exception as e:
        logger.exception(f"Error adding income: {e}")
        raise HTTPException(status_code=500, detail="Failed to add income")

# Delete an income entry.
@router.post("/income/{income_id}/delete")
@limiter.limit("10/minute")
def remove_income(
    request: Request,
    income_id: str,
    csrf_token: str = Form(...),
):
    try:
        user_id = require_user(request)
        require_csrf(request, csrf_token)

        try:
            delete_income(user_id, income_id)
        except DatabaseError as de:
            logger.error(f"Database error: {de}")
            raise HTTPException(status_code=500, detail=str(de))
        return RedirectResponse(url="/income", status_code=303)
    except (AuthError, HTTPException):
        raise
    except Exception as e:
        logger.error(f"Error deleting income: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete income")
