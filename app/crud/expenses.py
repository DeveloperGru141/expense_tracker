from typing import Any
from app.db.database import supabase
from app.exceptions import DatabaseError

def fetch_expenses(user_id: str, search: str = "") -> list[dict[str, Any]]:
    try:
        query = supabase.table("expenses").select("*").eq("user_id", user_id)

        if search:
            query = query.ilike("title", f"%{search}%")
            query = query.ilike("category", f"%{search}%")
            query = query.ilike("notes", f"%{search}%")

        response = query.order("expense_date", desc=True).execute()
        return response.data
    except Exception as e:
        raise DatabaseError("Error fetching expenses", original_exception=e)

def create_expense(user_id: str, data: dict[str, Any]) -> str:
    try:
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
    except Exception as e:
        raise DatabaseError("Error creating expense", original_exception=e)

def delete_expense(user_id: str, expense_id: str) -> str | None:
    try:
        response = supabase.table("expenses").select("receipt_image").eq("id", expense_id).eq("user_id", user_id).execute()
        receipt_image = response.data[0]["receipt_image"] if response.data and len(response.data) > 0 else None
        
        supabase.table("expenses").delete().eq("id", expense_id).eq("user_id", user_id).execute()
        return receipt_image
    except Exception as e:
        raise DatabaseError("Error deleting expense", original_exception=e)

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
