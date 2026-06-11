from typing import Any
from app.db.database import get_connection

def fetch_income(user_id: int, search: str = "") -> list[dict[str, Any]]:
    with get_connection() as connection:
        query = """
            SELECT id, title, amount, category, income_date, notes
            FROM income
            WHERE user_id = ?
        """
        params = [user_id]
        
        if search:
            query += " AND (title LIKE ? OR notes LIKE ? OR category LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
            
        query += " ORDER BY income_date DESC, id DESC"
        
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]

def create_income(user_id: int, data: dict[str, Any]) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO income (user_id, title, amount, category, income_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, data["title"], data["amount"], data["category"], data["income_date"], data["notes"]),
        )
        connection.commit()
        return cursor.lastrowid

def delete_income(user_id: int, income_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM income WHERE id = ? AND user_id = ?", (income_id, user_id))
        connection.commit()

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
