from fastapi import APIRouter, Request
from app.api.deps import require_user
from app.api.utils import render_page
from app.crud.expenses import fetch_expenses
from app.crud.analytics import build_summary, build_analytics, build_reports

router = APIRouter()

@router.get("/dashboard")
def dashboard(request: Request):
    user_id = require_user(request)
    from app.crud.recurring import process_recurring_expenses
    process_recurring_expenses(user_id)
    
    expenses = fetch_expenses(user_id)
    summary = build_summary(expenses)
    return render_page(
        request,
        "dashboard.html",
        "Dashboard",
        user_id,
        summary=summary,
        expenses=expenses[:5],
    )

@router.get("/analytics")
def analytics_page(request: Request):
    user_id = require_user(request)
    expenses = fetch_expenses(user_id)
    summary = build_summary(expenses)
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
    summary = build_summary(expenses)
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
    all_expenses = fetch_expenses(user_id)
    filtered = filter_expenses(all_expenses, date_from, date_to, category)
        
    summary = build_summary(filtered)
    reports = build_reports(filtered)
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
    from app.api.utils import get_settings
    
    all_expenses = fetch_expenses(user_id)
    filtered = filter_expenses(all_expenses, date_from, date_to, category)
    reports = build_reports(filtered)
    
    settings = get_settings(user_id)
    currency_code = settings.get("currency_code", "NGN").lower()
    
    if format == "csv":
        stream = StringIO()
        writer = csv.writer(stream)
        writer.writerow(["month", f"total_spent_{currency_code}"])
        for row in reports:
            writer.writerow([row["month"], f'{row["total"]:.2f}'])
        stream.seek(0)
        headers = {"Content-Disposition": "attachment; filename=expense_report.csv"}
        return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers=headers)
        
    elif format == "excel":
        df = pd.DataFrame(reports)
        df.columns = ["Month", f"Total Spent ({currency_code.upper()})"]
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        output.seek(0)
        headers = {"Content-Disposition": "attachment; filename=expense_report.xlsx"}
        return StreamingResponse(iter([output.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
        
    elif format == "pdf":
        output = BytesIO()
        p = canvas.Canvas(output, pagesize=letter)
        p.drawString(100, 750, f"Expense Report - {settings.get('display_name')}")
        p.drawString(100, 730, f"Currency: {currency_code.upper()}")
        y = 700
        p.drawString(100, y, "Month")
        p.drawString(300, y, "Total Spent")
        y -= 20
        for row in reports:
            p.drawString(100, y, str(row["month"]))
            p.drawString(300, y, f'{row["total"]:.2f}')
            y -= 20
            if y < 50:
                p.showPage()
                y = 750
        p.save()
        output.seek(0)
        headers = {"Content-Disposition": "attachment; filename=expense_report.pdf"}
        return StreamingResponse(iter([output.getvalue()]), media_type="application/pdf", headers=headers)
