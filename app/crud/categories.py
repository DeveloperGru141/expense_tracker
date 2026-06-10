from typing import Any
from app.db.database import get_connection

def fetch_categories(user_id: int) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, color, budget_limit FROM categories WHERE user_id = ? ORDER BY name",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]

def update_category_budget(user_id: int, category_id: int, budget_limit: float) -> None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE categories SET budget_limit = ? WHERE id = ? AND user_id = ?",
            (budget_limit, category_id, user_id),
        )
        connection.commit()
