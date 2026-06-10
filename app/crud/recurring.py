from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from app.db.database import get_connection
from typing import Any

def process_recurring_expenses(user_id: int) -> None:
    today = date.today()
    with get_connection() as connection:
        recurrings = connection.execute(
            "SELECT * FROM recurring_expenses WHERE user_id = ? AND next_occurrence <= ?",
            (user_id, today.isoformat()),
        ).fetchall()

        for rec in recurrings:
            next_date = date.fromisoformat(rec["next_occurrence"])
            while next_date <= today:
                connection.execute(
                    """
                    INSERT INTO expenses (user_id, title, amount, category, expense_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, rec["title"], rec["amount"], rec["category"], next_date.isoformat(), rec["notes"]),
                )
                
                if rec["frequency"] == "daily":
                    next_date += timedelta(days=1)
                elif rec["frequency"] == "weekly":
                    next_date += timedelta(weeks=1)
                elif rec["frequency"] == "monthly":
                    next_date += relativedelta(months=1)
                elif rec["frequency"] == "yearly":
                    next_date += relativedelta(years=1)
                else:
                    break

            connection.execute(
                "UPDATE recurring_expenses SET next_occurrence = ? WHERE id = ?",
                (next_date.isoformat(), rec["id"]),
            )
        connection.commit()

def fetch_recurring_expenses(user_id: int) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM recurring_expenses WHERE user_id = ? ORDER BY next_occurrence", (user_id,)).fetchall()
    return [dict(row) for row in rows]
