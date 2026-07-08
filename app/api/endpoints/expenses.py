import secrets
import logging
from datetime import date
from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.core.security import require_csrf
from app.core.config import templates
from app.crud.expenses import fetch_expenses, create_expense, delete_expense
from app.crud.recurring import process_recurring_expenses
from app.crud.analytics import build_summary
from app.crud.income import fetch_income
from app.api.utils import render_page, validate_redirect_url
from app.exceptions import AuthError, DatabaseError
from app.core.limiter import limiter
from app.storage import upload_receipt, delete_receipt, enrich_expense_with_receipt

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_TITLE_LENGTH = 200
MAX_NOTES_LENGTH = 1000
MAX_SEARCH_LENGTH = 100

# Show the expenses listing page with optional search.
@router.get("/expenses")
@limiter.limit("30/minute")
def expenses_page(request: Request, q: str = ""):
    try:
        user_id = require_user(request)
        q = q[:MAX_SEARCH_LENGTH] if q else ""
        process_recurring_expenses(user_id)
        expenses = fetch_expenses(user_id, search=q)
        expenses = [enrich_expense_with_receipt(e) for e in expenses]
        summary = build_summary(expenses)

        return render_page(
            request,
            "expenses.html",
            "Expenses",
            user_id,
            summary=summary,
            expenses=expenses,
            search_query=q,
        )
    except (AuthError, HTTPException):
        raise
    except DatabaseError as de:
        logger.error(f"Database error loading expenses: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error loading expenses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Handle adding a new expense with optional receipt upload.
@router.post("/expenses")
@limiter.limit("10/minute")
async def add_expense(
    request: Request,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    expense_date: str = Form(...),
    notes: str = Form(""),
    next_url: str = Form("/expenses"),
    csrf_token: str = Form(...),
    receipt: UploadFile = File(None)
):
    try:
        user_id = require_user(request)
        require_csrf(request, csrf_token)

        title = title.strip()[:MAX_TITLE_LENGTH]
        notes = notes.strip()[:MAX_NOTES_LENGTH]
        category = category.strip()[:100]
        next_url = validate_redirect_url(next_url[:500])

        if not title:
            raise HTTPException(status_code=422, detail="Title is required")
        if amount <= 0:
            raise HTTPException(status_code=422, detail="Amount must be positive")
        if not category:
            raise HTTPException(status_code=422, detail="Category is required")

        try:
            date.fromisoformat(expense_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format")

        receipt_image = ""
        if receipt and receipt.filename:
            from PIL import Image
            import io

            content = await receipt.read()
            if len(content) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Receipt image too large (max 10MB)")

            try:
                img = Image.open(io.BytesIO(content))
                img.verify()
                img = Image.open(io.BytesIO(content))
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid image file")

            ext = receipt.filename.split(".")[-1].lower()
            if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
                 ext = img.format.lower() if img.format else "png"

            filename = f"{secrets.token_hex(8)}.{ext}"
            content_type = f"image/{ext.replace('jpg', 'jpeg')}"
            stored_path = upload_receipt(user_id, filename, content, content_type)
            if stored_path:
                receipt_image = stored_path

        expense_data = {
            "title": title,
            "amount": amount,
            "category": category,
            "expense_date": expense_date,
            "notes": notes,
            "receipt_image": receipt_image
        }

        logger.info(f"Adding expense for user {user_id}: {title}")
        create_expense(user_id, expense_data)

        return RedirectResponse(url=next_url, status_code=303)
    except (AuthError, HTTPException):
        raise
    except DatabaseError as de:
        logger.error(f"Database error adding expense: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error adding expense: {e}")
        raise HTTPException(status_code=500, detail="Failed to add expense")

# Delete an expense and its associated receipt.
@router.post("/expenses/{expense_id}/delete")
def remove_expense(
    request: Request,
    expense_id: str,
    next_url: str = Form("/expenses"),
    csrf_token: str = Form(...),
):
    try:
        user_id = require_user(request)
        require_csrf(request, csrf_token)

        receipt_image = delete_expense(user_id, expense_id)
        if receipt_image:
            delete_receipt(receipt_image)

        next_url = validate_redirect_url(next_url[:500])
        return RedirectResponse(url=next_url, status_code=303)
    except (AuthError, HTTPException):
        raise
    except DatabaseError as de:
        logger.error(f"Database error deleting expense: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error deleting expense: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete expense")
