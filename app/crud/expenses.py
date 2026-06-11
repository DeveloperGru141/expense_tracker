from typing import Any
from app.db.database import supabase

def fetch_expenses(user_id: int, search: str = "") -> list[dict[str, Any]]:
    query = supabase.table("expenses").select("*").eq("user_id", user_id)
    
    if search:
        # Supabase's OR filter is a bit different, using a simple ILIKE search on title for now
        query = query.ilike("title", f"%{search}%")
        
    response = query.order("expense_date", desc=True).execute()
    return response.data

def create_expense(user_id: int, data: dict[str, Any]) -> int:
    response = supabase.table("expenses").insert({
        "user_id": user_id,
        "title": data["title"],
        "amount": data["amount"],
        "category": data["category"],
        "expense_date": data["expense_date"],
        "notes": data["notes"],
        "receipt_image": data.get("receipt_image", "")
    }).execute()
    return response.data[0]["id"]

def delete_expense(user_id: int, expense_id: int) -> str | None:
    # First get the receipt_image
    response = supabase.table("expenses").select("receipt_image").eq("id", expense_id).eq("user_id", user_id).execute()
    receipt_image = response.data[0]["receipt_image"] if response.data else None
    
    # Then delete
    supabase.table("expenses").delete().eq("id", expense_id).eq("user_id", user_id).execute()
    return receipt_image

def filter_expenses(
    expenses: list[dict[str, Any]],
    date_from: str = "",
    date_to: str = "",
    category: str = "",
) -> list[dict[str, Any]]:
    filtered = expenses
    if date_from:
        filtered = [item for item in filtered if item["expense_date"] >= date_from]
    if date_to:
        filtered = [item for item in filtered if item["expense_date"] <= date_to]
    if category:
        filtered = [item for item in filtered if item["category"] == category]
    return filtered
