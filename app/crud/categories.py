from typing import Any
from app.db.database import get_supabase
from app.exceptions import DatabaseError

# Fetch all categories for a user.
def fetch_categories(user_id: str) -> list[dict[str, Any]]:
    try:
        # Fetch categories specific to the user
        response = get_supabase().table("categories").select("*").eq("user_id", user_id).order("name").execute()
        return response.data
    except Exception as e:
        raise DatabaseError("Error fetching categories", original_exception=e)

# Update the budget limit for a specific category.
def update_category_budget(user_id: str, category_id: str, budget_limit: float) -> None:
    # Note: If categories are global, this might need to change to
    # user-specific settings if users have different budgets for the same global category.
    # For now, keeping the update restricted to the user.
    try:
        get_supabase().table("categories").update({"budget_limit": budget_limit}).eq("id", category_id).eq("user_id", user_id).execute()
    except Exception as e:
        raise DatabaseError("Error updating category budget", original_exception=e)
