from fastapi import APIRouter, Request, HTTPException
from app.api.deps import require_user
from app.api.utils import render_page
from app.crud.expenses import fetch_expenses
from app.crud.analytics import build_summary, build_analytics, build_reports
from app.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard")
def dashboard(request: Request):
    try:
        user_id = require_user(request)
        from app.crud.recurring import process_recurring_expenses
        try:
            process_recurring_expenses(user_id)
        except Exception as e:
            raise DatabaseError("Failed to process recurring expenses", original_exception=e)
        
        from app.crud.categories import fetch_categories
        from app.crud.income import fetch_income
        try:
            categories = fetch_categories(user_id)
            expenses = fetch_expenses(user_id)
            income = fetch_income(user_id)
        except Exception as e:
            raise DatabaseError("Failed to fetch dashboard data", original_exception=e)
            
        summary = build_summary(expenses, categories, income)
        return render_page(
            request,
            "dashboard.html",
            "Dashboard",
            user_id,
            summary=summary,
            expenses=expenses[:5],
        )
    except DatabaseError as de:
        logger.error(f"Database error loading dashboard: {de}")
        raise HTTPException(status_code=500, detail=str(de))
    except Exception as e:
        logger.exception(f"Unexpected error loading dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analytics")
def analytics_page(request: Request):
    user_id = require_user(request)
    expenses = fetch_expenses(user_id)
    from app.crud.income import fetch_income
    income = fetch_income(user_id)
    summary = build_summary(expenses, income=income)
    analytics_data = build_analytics(expenses, summary)
    return render_page(
        request,
        "analytics.html",
        "Analytics",
        user_id,
        summary=summary,
        analytics=analytics_data["categories"],
    )

@router.get("/ai-insights")
def ai_insights_page(request: Request):
    user_id = require_user(request)
    expenses = fetch_expenses(user_id)
    from app.crud.income import fetch_income
    income = fetch_income(user_id)
    summary = build_summary(expenses, income=income)
    analytics_data = build_analytics(expenses, summary)
    return render_page(
        request,
        "ai_insights.html",
        "AI Insights",
        user_id,
        summary=summary,
        analytics=analytics_data["categories"],
        insights=analytics_data["insights"],
    )

@router.get("/reports")
def reports_page(
    request: Request,
    date_from: str = "",
    date_to: str = "",
    category: str = "",
):
    user_id = require_user(request)
    from app.crud.expenses import fetch_expenses, filter_expenses
    from app.crud.income import fetch_income, filter_income
    
    all_expenses = fetch_expenses(user_id)
    filtered_expenses = filter_expenses(all_expenses, date_from, date_to, category)
    
    all_income = fetch_income(user_id)
    filtered_income = filter_income(all_income, date_from, date_to, category)
        
    summary = build_summary(filtered_expenses, income=filtered_income)
    reports = build_reports(filtered_expenses, filtered_income)
    return render_page(
        request,
        "reports.html",
        "Reports",
        user_id,
        summary=summary,
        reports=reports,
        filters={
            "date_from": date_from,
            "date_to": date_to,
            "category": category,
        },
    )

import csv
from io import StringIO, BytesIO
from fastapi.responses import StreamingResponse
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@router.get("/reports/export")
def export_reports(
    request: Request,
    date_from: str = "",
    date_to: str = "",
    category: str = "",
    format: str = "csv"
):
    user_id = require_user(request)
    from app.crud.expenses import fetch_expenses, filter_expenses
    from app.crud.income import fetch_income, filter_income
    from app.api.utils import get_settings
    
    all_expenses = fetch_expenses(user_id)
    filtered_expenses = filter_expenses(all_expenses, date_from, date_to, category)
    
    all_income = fetch_income(user_id)
    filtered_income = filter_income(all_income, date_from, date_to, category)
    
    reports = build_reports(filtered_expenses, filtered_income)
    
    settings = get_settings(user_id)
    currency_code = settings.get("currency_code", "NGN").lower()
    
    if format == "csv":
        stream = StringIO()
        writer = csv.writer(stream)
        writer.writerow(["month", f"spent_{currency_code}", f"income_{currency_code}", f"balance_{currency_code}"])
        for row in reports:
            writer.writerow([row["month"], f'{row["spent"]:.2f}', f'{row["income"]:.2f}', f'{row["balance"]:.2f}'])
        stream.seek(0)
        headers = {"Content-Disposition": "attachment; filename=financial_report.csv"}
        return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers=headers)
        
    elif format == "excel":
        df = pd.DataFrame(reports)
        df.columns = ["Month", f"Spent ({currency_code.upper()})", f"Income ({currency_code.upper()})", f"Balance ({currency_code.upper()})"]
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        output.seek(0)
        headers = {"Content-Disposition": "attachment; filename=financial_report.xlsx"}
        return StreamingResponse(iter([output.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
        
    elif format == "pdf":
        output = BytesIO()
        p = canvas.Canvas(output, pagesize=letter)
        p.drawString(100, 750, f"Financial Report - {settings.get('display_name')}")
        p.drawString(100, 730, f"Currency: {currency_code.upper()}")
        y = 700
        p.drawString(50, y, "Month")
        p.drawString(150, y, "Spent")
        p.drawString(250, y, "Income")
        p.drawString(350, y, "Balance")
        y -= 20
        for row in reports:
            p.drawString(50, y, str(row["month"]))
            p.drawString(150, y, f'{row["spent"]:.2f}')
            p.drawString(250, y, f'{row["income"]:.2f}')
            p.drawString(350, y, f'{row["balance"]:.2f}')
            y -= 20
            if y < 50:
                p.showPage()
                y = 750
        p.save()
        output.seek(0)
        headers = {"Content-Disposition": "attachment; filename=financial_report.pdf"}
        return StreamingResponse(iter([output.getvalue()]), media_type="application/pdf", headers=headers)
