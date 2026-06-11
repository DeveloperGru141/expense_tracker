import secrets
from datetime import date
from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.core.security import require_csrf
from app.core.config import templates, UPLOAD_DIR
from app.crud.expenses import fetch_expenses, create_expense, delete_expense
from app.crud.recurring import process_recurring_expenses
from app.crud.analytics import build_summary

router = APIRouter()

@router.get("/expenses")
def expenses_page(request: Request, q: str = ""):
    user_id = require_user(request)
    process_recurring_expenses(user_id)
    expenses = fetch_expenses(user_id, search=q)
    summary = build_summary(expenses)
    
    from app.api.utils import render_page
    return render_page(
        request,
        "expenses.html",
        "Expenses",
        user_id,
        summary=summary,
        expenses=expenses,
        search_query=q,
    )

from app.core.limiter import limiter

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
    user_id = require_user(request)
    require_csrf(request, csrf_token)
    
    try:
        date.fromisoformat(expense_date)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format")

    receipt_filename = ""
    if receipt and receipt.filename:
        # Step 4: Security - Advanced File Validation
        from PIL import Image
        import io
        
        content = await receipt.read()
        try:
            img = Image.open(io.BytesIO(content))
            img.verify() # Verify it's an image
            # Re-read for saving since verify() can close the file or move pointer
            img = Image.open(io.BytesIO(content))
            img.format.lower() # Check format
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")

        ext = receipt.filename.split(".")[-1].lower()
        if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
             ext = img.format.lower() if img.format else "png"

        receipt_filename = f"{secrets.token_hex(8)}.{ext}"
        with open(UPLOAD_DIR / receipt_filename, "wb") as f:
            f.write(content)

    create_expense(user_id, {
        "title": title.strip(),
        "amount": amount,
        "category": category.strip(),
        "expense_date": expense_date,
        "notes": notes.strip(),
        "receipt_image": receipt_filename
    })
    
    return RedirectResponse(url=next_url, status_code=303)

@router.post("/expenses/{expense_id}/delete")
def remove_expense(
    request: Request,
    expense_id: int,
    next_url: str = Form("/expenses"),
    csrf_token: str = Form(...),
):
    user_id = require_user(request)
    require_csrf(request, csrf_token)
    
    receipt_image = delete_expense(user_id, expense_id)
    if receipt_image:
        img_path = UPLOAD_DIR / receipt_image
        if img_path.exists():
            img_path.unlink()
            
    return RedirectResponse(url=next_url, status_code=303)
