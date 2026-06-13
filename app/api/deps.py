from fastapi import Request
from app.db.database import supabase
from app.exceptions import AuthError

def get_authenticated_user_id(request: Request) -> str | None:
    token = request.cookies.get("supabase_auth_token")
    if not token:
        return None

    try:
        auth_response = supabase.auth.get_user(token)
        if not auth_response or not auth_response.user:
            return None
        supabase.postgrest.auth(token)
        return auth_response.user.id
    except Exception:
        return None

def require_user(request: Request) -> str:
    user_id = get_authenticated_user_id(request)
    if user_id is None:
        raise AuthError("Not authenticated")
    return user_id
