from app.db.database import get_supabase
from app.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)

# Permanently delete a user and all associated data.
def delete_user_account(user_id: str) -> None:
    """
    Permanently deletes all data associated with the user, including the user profile.
    This action is irreversible.
    """
    # Note: If foreign keys are set to ON DELETE CASCADE, 
    # deleting from 'users' would be enough. 
    # To be safe and explicit, we clear dependent data first.
    tables_to_clear = [
        "expenses",
        "income",
        "recurring_expenses",
        "recurring_income",
        "categories",
        "settings",
        "users"
    ]
    
    try:
        for table in tables_to_clear:
            logger.info(f"Deleting data from table {table} for user {user_id}")
            if table == "users":
                get_supabase().table(table).delete().eq("id", user_id).execute()
            else:
                get_supabase().table(table).delete().eq("user_id", user_id).execute()
    except Exception as e:
        logger.error(f"Error deleting account for user {user_id}: {e}")
        raise DatabaseError(f"Failed to permanently delete account", original_exception=e)
