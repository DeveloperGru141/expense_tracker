from typing import Any
from collections import defaultdict

# Build a summary of totals, categories, and daily trends.
def build_summary(expenses: list[dict[str, Any]], categories: list[dict[str, Any]] = None, income: list[dict[str, Any]] = None) -> dict[str, Any]:
    total_spent = sum(item["amount"] for item in expenses)
    total_income = sum(item["amount"] for item in income) if income else 0.0
    balance = total_income - total_spent

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

    # Map colors to top categories for the chart
    category_colors = []
    if categories:
        cat_color_map = {cat["name"]: cat.get("color", "#64748b") for cat in categories}
        for name, _ in top_categories:
            category_colors.append(cat_color_map.get(name, "#64748b"))
    else:
        category_colors = ['#ef4444', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6', '#10b981', '#64748b']

    return {
        "count": len(expenses),
        "total": total_spent,
        "total_income": total_income,
        "balance": balance,
        "categories": top_categories,
        "category_progress": category_progress,
        "top_category": top_categories[0][0] if top_categories else "None yet",
        "chart_data": {
            "labels": trend_labels,
            "values": trend_values,
            "category_labels": [c for c, v in top_categories],
            "category_values": [v for c, v in top_categories],
            "category_colors": category_colors,
        }
    }

# Build category breakdown and spending insights.
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

# Build monthly report data from expenses and income.
def build_reports(expenses: list[dict[str, Any]], income: list[dict[str, Any]] = None) -> list[dict[str, Any]]:
    monthly_data: dict[str, dict[str, float]] = defaultdict(lambda: {"spent": 0.0, "income": 0.0})
    for item in expenses:
        month_key = item["expense_date"][:7]
        monthly_data[month_key]["spent"] += item["amount"]
    
    if income:
        for item in income:
            month_key = item["income_date"][:7]
            monthly_data[month_key]["income"] += item["amount"]
            
    return [
        {"month": month, "spent": data["spent"], "income": data["income"], "balance": data["income"] - data["spent"]}
        for month, data in sorted(monthly_data.items(), reverse=True)
    ]
