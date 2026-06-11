from typing import Any
from app.db.database import supabase

def fetch_income(user_id: int, search: str = "") -> list[dict[str, Any]]:
    query = supabase.table("income").select("*").eq("user_id", user_id)
    
    if search:
        query = query.ilike("title", f"%{search}%")
        
    response = query.order("income_date", desc=True).execute()
    return response.data

def create_income(user_id: int, data: dict[str, Any]) -> int:
    response = supabase.table("income").insert({
        "user_id": user_id,
        "title": data["title"],
        "amount": data["amount"],
        "category": data["category"],
        "income_date": data["income_date"],
        "notes": data["notes"]
    }).execute()
    return response.data[0]["id"]

def delete_income(user_id: int, income_id: int) -> None:
    supabase.table("income").delete().eq("id", income_id).eq("user_id", user_id).execute()

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
