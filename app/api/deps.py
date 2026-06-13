from fastapi import Request
from app.db.database import supabase
from app.exceptions import AuthError

def get_authenticated_user_id(request: Request) -> str | None:
    try:
        auth_headers = getattr(supabase.postgrest, "headers", {})
        auth_headers.pop("Authorization", None)
    except Exception:
        pass

    token = request.cookies.get("supabase_auth_token")
    if not token:
        return None
    
    try:
        user = supabase.auth.get_user(token)
        supabase.postgrest.auth(token)
        return user.user.id
    except Exception:
        return None

def require_user(request: Request) -> str:
    user_id = get_authenticated_user_id(request)
    if user_id is None:
        raise AuthError("Not authenticated")
    return user_id
