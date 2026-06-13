import secrets
import logging
from datetime import date
from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.core.security import require_csrf
from app.core.config import templates, UPLOAD_DIR
from app.crud.expenses import fetch_expenses, create_expense, delete_expense
from app.crud.recurring import process_recurring_expenses
from app.crud.analytics import build_summary
from app.crud.income import fetch_income
from app.api.utils import render_page
from app.exceptions import DatabaseError
from app.core.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/expenses")
def expenses_page(request: Request, q: str = ""):
    try:
        user_id = require_user(request)
        process_recurring_expenses(user_id)
        expenses = fetch_expenses(user_id, search=q)
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
    except DatabaseError as de:
        logger.error(f"Database error loading expenses: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error loading expenses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
        
        if amount <= 0:
            raise HTTPException(status_code=422, detail="Amount must be positive")
        
        try:
            date.fromisoformat(expense_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format")

        receipt_filename = ""
        if receipt and receipt.filename:
            from PIL import Image
            import io
            
            content = await receipt.read()
            try:
                img = Image.open(io.BytesIO(content))
                img.verify() 
                img = Image.open(io.BytesIO(content))
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid image file")

            ext = receipt.filename.split(".")[-1].lower()
            if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
                 ext = img.format.lower() if img.format else "png"

            receipt_filename = f"{secrets.token_hex(8)}.{ext}"
            with open(UPLOAD_DIR / receipt_filename, "wb") as f:
                f.write(content)

        expense_data = {
            "title": title.strip(),
            "amount": amount,
            "category": category.strip(),
            "expense_date": expense_date,
            "notes": notes.strip(),
            "receipt_image": receipt_filename
        }
        
        logger.info(f"Adding expense for user {user_id}: {title}")
        create_expense(user_id, expense_data)
        
        return RedirectResponse(url=next_url, status_code=303)
    except HTTPException:
        raise
    except DatabaseError as de:
        logger.error(f"Database error adding expense: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error adding expense: {e}")
        raise HTTPException(status_code=500, detail="Failed to add expense")

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
            img_path = UPLOAD_DIR / receipt_image
            if img_path.exists():
                img_path.unlink()
                
        return RedirectResponse(url=next_url, status_code=303)
    except DatabaseError as de:
        logger.error(f"Database error deleting expense: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error deleting expense: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete expense")
