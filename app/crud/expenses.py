from typing import Any
from app.db.database import get_connection

def fetch_expenses(user_id: int, search: str = "") -> list[dict[str, Any]]:
    with get_connection() as connection:
        query = """
            SELECT id, title, amount, category, expense_date, notes, receipt_image
            FROM expenses
            WHERE user_id = ?
        """
        params = [user_id]
        
        if search:
            query += " AND (title LIKE ? OR notes LIKE ? OR category LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
            
        query += " ORDER BY expense_date DESC, id DESC"
        
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]

def create_expense(user_id: int, data: dict[str, Any]) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO expenses (user_id, title, amount, category, expense_date, notes, receipt_image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, data["title"], data["amount"], data["category"], data["expense_date"], data["notes"], data.get("receipt_image", "")),
        )
        connection.commit()
        return cursor.lastrowid

def delete_expense(user_id: int, expense_id: int) -> str | None:
    with get_connection() as connection:
        row = connection.execute("SELECT receipt_image FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id)).fetchone()
        receipt_image = row["receipt_image"] if row else None
        connection.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
        connection.commit()
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
