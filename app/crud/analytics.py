from typing import Any
from collections import defaultdict

def build_summary(expenses: list[dict[str, Any]], categories: list[dict[str, Any]] = None) -> dict[str, Any]:
    total = sum(item["amount"] for item in expenses)
    by_category: dict[str, float] = {}
    for item in expenses:
        by_category[item["category"]] = by_category.get(item["category"], 0.0) + item["amount"]

    top_categories = sorted(
        by_category.items(),
        key=lambda entry: entry[1],
        reverse=True,
    )

    # Budget progress per category
    category_progress = []
    if categories:
        for cat in categories:
            spent = by_category.get(cat["name"], 0.0)
            limit = cat.get("budget_limit", 0)
            percentage = (spent / limit * 100) if limit > 0 else 0
            category_progress.append({
                "name": cat["name"],
                "spent": spent,
                "limit": limit,
                "percentage": min(percentage, 100),
                "is_over": spent > limit if limit > 0 else False,
                "color": cat.get("color", "#0f766e")
            })

    daily_totals: dict[str, float] = defaultdict(float)
    for item in expenses:
        daily_totals[item["expense_date"]] += item["amount"]
    
    sorted_dates = sorted(daily_totals.keys())
    trend_labels = sorted_dates[-30:]
    trend_values = [daily_totals[d] for d in trend_labels]

    return {
        "count": len(expenses),
        "total": total,
        "categories": top_categories,
        "category_progress": category_progress,
        "top_category": top_categories[0][0] if top_categories else "None yet",
        "chart_data": {
            "labels": trend_labels,
            "values": trend_values,
            "category_labels": [c for c, v in top_categories],
            "category_values": [v for c, v in top_categories],
        }
    }

def build_analytics(expenses: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    total = summary["total"] or 0.0
    category_data = []
    
    for category, amount in summary["categories"]:
        percentage = 0.0 if total == 0 else (amount / total) * 100
        category_data.append(
            {
                "category": category,
                "amount": amount,
                "percentage": percentage,
            }
        )

    insights = []
    if total > 0:
        top_cat = summary["top_category"]
        top_amount = summary["categories"][0][1]
        insights.append(f"Your highest spending category is {top_cat}, accounting for { (top_amount/total*100):.1f}% of your budget.")
        
        if len(summary["categories"]) > 1:
            avg = total / len(summary["categories"])
            if top_amount > avg * 1.5:
                insights.append(f"Spending in {top_cat} is significantly higher than your average category spend. You might want to review these entries.")

    return {
        "categories": category_data,
        "insights": insights
    }

def build_reports(expenses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    monthly_totals: dict[str, float] = defaultdict(float)
    for item in expenses:
        month_key = item["expense_date"][:7]
        monthly_totals[month_key] += item["amount"]
    return [
        {"month": month, "total": total}
        for month, total in sorted(monthly_totals.items(), reverse=True)
    ]
