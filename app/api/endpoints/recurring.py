from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.api.deps import require_user
from app.api.utils import render_page
from app.core.security import require_csrf
from app.crud.expenses import fetch_expenses
from app.crud.analytics import build_summary
from app.crud.recurring import process_recurring_expenses, fetch_recurring_expenses
from app.db.database import get_connection

router = APIRouter()

@router.get("/recurring")
def recurring_page(request: Request):
    user_id = require_user(request)
    process_recurring_expenses(user_id)
    recurrings = fetch_recurring_expenses(user_id)
    summary = build_summary(fetch_expenses(user_id))
    return render_page(
        request,
        "recurring.html",
        "Recurring",
        user_id,
        recurrings=recurrings,
        summary=summary,
    )

@router.post("/recurring")
def create_recurring(
    request: Request,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    frequency: str = Form(...),
    start_date: str = Form(...),
    notes: str = Form(""),
    csrf_token: str = Form(...),
):
    user_id = require_user(request)
    require_csrf(request, csrf_token)
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO recurring_expenses (user_id, title, amount, category, frequency, start_date, next_occurrence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, title.strip(), amount, category.strip(), frequency, start_date, start_date, notes.strip()),
        )
        connection.commit()
    return RedirectResponse(url="/recurring", status_code=303)

@router.post("/recurring/{recurring_id}/delete")
def delete_recurring(request: Request, recurring_id: int, csrf_token: str = Form(...)):
    user_id = require_user(request)
    require_csrf(request, csrf_token)
    with get_connection() as connection:
        connection.execute("DELETE FROM recurring_expenses WHERE id = ? AND user_id = ?", (recurring_id, user_id))
        connection.commit()
    return RedirectResponse(url="/recurring", status_code=303)
