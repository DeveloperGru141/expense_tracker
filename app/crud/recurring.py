from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from app.db.database import supabase
from typing import Any
from app.exceptions import DatabaseError

def process_recurring_expenses(user_id: str) -> None:
    try:
        today = date.today()
        
        # Optimization: Check if already processed today
        setting = supabase.table("settings").select("value").eq("user_id", user_id).eq("key", "last_processed_recurring").execute()
        if setting.data and setting.data[0]["value"] == today.isoformat():
            return

        recurrings = supabase.table("recurring_expenses").select("*").eq("user_id", user_id).lte("next_occurrence", today.isoformat()).execute().data

        for rec in recurrings:
            next_date = date.fromisoformat(rec["next_occurrence"])
            while next_date <= today:
                supabase.table("expenses").insert({
                    "user_id": user_id, 
                    "title": rec["title"], 
                    "amount": rec["amount"], 
                    "category": rec["category"], 
                    "expense_date": next_date.isoformat(), 
                    "notes": rec["notes"]
                }).execute()
                
                if rec["frequency"] == "daily": next_date += timedelta(days=1)
                elif rec["frequency"] == "weekly": next_date += timedelta(weeks=1)
                elif rec["frequency"] == "monthly": next_date += relativedelta(months=1)
                elif rec["frequency"] == "yearly": next_date += relativedelta(years=1)
                else: break

            supabase.table("recurring_expenses").update({"next_occurrence": next_date.isoformat()}).eq("id", rec["id"]).execute()
            
        # Process recurring income
        recurring_income = supabase.table("recurring_income").select("*").eq("user_id", user_id).lte("next_occurrence", today.isoformat()).execute().data

        for rec in recurring_income:
            next_date = date.fromisoformat(rec["next_occurrence"])
            while next_date <= today:
                supabase.table("income").insert({
                    "user_id": user_id, 
                    "title": rec["title"], 
                    "amount": rec["amount"], 
                    "category": rec["category"], 
                    "income_date": next_date.isoformat(), 
                    "notes": rec["notes"]
                }).execute()
                
                if rec["frequency"] == "daily": next_date += timedelta(days=1)
                elif rec["frequency"] == "weekly": next_date += timedelta(weeks=1)
                elif rec["frequency"] == "monthly": next_date += relativedelta(months=1)
                elif rec["frequency"] == "yearly": next_date += relativedelta(years=1)
                else: break

            supabase.table("recurring_income").update({"next_occurrence": next_date.isoformat()}).eq("id", rec["id"]).execute()

        # Update last processed date using upsert
        supabase.table("settings").upsert({"user_id": user_id, "key": "last_processed_recurring", "value": today.isoformat()}).execute()
    except Exception as e:
        raise DatabaseError("Error processing recurring expenses", original_exception=e)

def fetch_recurring_expenses(user_id: str) -> list[dict[str, Any]]:
    try:
        return supabase.table("recurring_expenses").select("*").eq("user_id", user_id).order("next_occurrence").execute().data
    except Exception as e:
        raise DatabaseError("Error fetching recurring expenses", original_exception=e)

def fetch_recurring_income(user_id: str) -> list[dict[str, Any]]:
    try:
        return supabase.table("recurring_income").select("*").eq("user_id", user_id).order("next_occurrence").execute().data
    except Exception as e:
        raise DatabaseError("Error fetching recurring income", original_exception=e)
