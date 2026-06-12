from typing import Any
from app.db.database import supabase
from app.exceptions import DatabaseError

def fetch_categories(user_id: int | None = None) -> list[dict[str, Any]]:
    try:
        # Fetch all global categories, ignoring user_id
        response = supabase.table("categories").select("*").order("name").execute()
        return response.data
    except Exception as e:
        raise DatabaseError("Error fetching categories", original_exception=e)

def update_category_budget(user_id: int, category_id: int, budget_limit: float) -> None:
    # Note: If categories are global, this might need to change to
    # user-specific settings if users have different budgets for the same global category.
    # For now, keeping the update restricted to the user.
    try:
        supabase.table("categories").update({"budget_limit": budget_limit}).eq("id", category_id).eq("user_id", user_id).execute()
    except Exception as e:
        raise DatabaseError("Error updating category budget", original_exception=e)
