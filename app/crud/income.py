from typing import Any
from app.db.database import supabase
from app.exceptions import DatabaseError

def fetch_income(user_id: str, search: str = "") -> list[dict[str, Any]]:
    try:
        query = supabase.table("income").select("*").eq("user_id", user_id)
        
        if search:
            query = query.ilike("title", f"%{search}%")
            
        response = query.order("income_date", desc=True).execute()
        return response.data
    except Exception as e:
        raise DatabaseError("Error fetching income", original_exception=e)

def create_income(user_id: str, data: dict[str, Any]) -> str:
    try:
        response = supabase.table("income").insert({
            "user_id": user_id,
            "title": data["title"],
            "amount": data["amount"],
            "category": data["category"],
            "income_date": data["income_date"],
            "notes": data["notes"]
        }).execute()
        return response.data[0]["id"]
    except Exception as e:
        raise DatabaseError("Error creating income", original_exception=e)

def delete_income(user_id: str, income_id: str) -> None:
    try:
        supabase.table("income").delete().eq("id", income_id).eq("user_id", user_id).execute()
    except Exception as e:
        raise DatabaseError("Error deleting income", original_exception=e)

def filter_income(
    income_list: list[dict[str, Any]],
    date_from: str = "",
    date_to: str = "",
    category: str = "",
) -> list[dict[str, Any]]:
    filtered = income_list
    if date_from:
        filtered = [item for item in filtered if item["income_date"] >= date_from]
    if date_to:
        filtered = [item for item in filtered if item["income_date"] <= date_to]
    if category:
        filtered = [item for item in filtered if item["category"] == category]
    return filtered
