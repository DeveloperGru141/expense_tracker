import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def seed_categories(user_id: str):
    categories = [
        {"name": "Food", "color": "#f59e0b", "budget_limit": 50000, "user_id": user_id},
        {"name": "Transport", "color": "#3b82f6", "budget_limit": 20000, "user_id": user_id},
        {"name": "Housing", "color": "#ef4444", "budget_limit": 150000, "user_id": user_id},
        {"name": "Utilities", "color": "#8b5cf6", "budget_limit": 30000, "user_id": user_id},
        {"name": "Entertainment", "color": "#ec4899", "budget_limit": 20000, "user_id": user_id},
    ]
    
    for cat in categories:
        supabase.table("categories").insert(cat).execute()
        print(f"Added category: {cat['name']}")

if __name__ == "__main__":
    # You need to replace this with a valid user UUID from your Supabase dashboard
    user_id = input("Enter the user UUID to seed categories for: ")
    seed_categories(user_id)
