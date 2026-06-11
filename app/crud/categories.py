from typing import Any
from app.db.database import supabase

def fetch_categories(user_id: int) -> list[dict[str, Any]]:
    response = supabase.table("categories").select("*").eq("user_id", user_id).order("name").execute()
    return response.data

def update_category_budget(user_id: int, category_id: int, budget_limit: float) -> None:
    supabase.table("categories").update({"budget_limit": budget_limit}).eq("id", category_id).eq("user_id", user_id).execute()
