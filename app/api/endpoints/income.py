from datetime import date
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.core.security import require_csrf
from app.crud.income import fetch_income, create_income, delete_income
from app.crud.recurring import process_recurring_expenses
from app.api.utils import render_page

router = APIRouter()

@router.get("/income")
def income_page(request: Request, q: str = ""):
    user_id = require_user(request)
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

@router.post("/income")
def add_income(
    request: Request,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    income_date: str = Form(...),
    notes: str = Form(""),
    csrf_token: str = Form(...),
):
    user_id = require_user(request)
    require_csrf(request, csrf_token)
    
    try:
        date.fromisoformat(income_date)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format")

    create_income(user_id, {
        "title": title.strip(),
        "amount": amount,
        "category": category.strip(),
        "income_date": income_date,
        "notes": notes.strip(),
    })
    
    return RedirectResponse(url="/income", status_code=303)

@router.post("/income/{income_id}/delete")
def remove_income(
    request: Request,
    income_id: int,
    csrf_token: str = Form(...),
):
    user_id = require_user(request)
    require_csrf(request, csrf_token)
    
    delete_income(user_id, income_id)
    return RedirectResponse(url="/income", status_code=303)
