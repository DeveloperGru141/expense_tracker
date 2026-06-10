from fastapi import Request, HTTPException
from app.core.security import verify_signed_value
from app.core.config import AUTH_COOKIE

def get_authenticated_user_id(request: Request) -> int | None:
    user_id_str = verify_signed_value(request.cookies.get(AUTH_COOKIE))
    return int(user_id_str) if user_id_str else None

def require_user(request: Request) -> int:
    user_id = get_authenticated_user_id(request)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_id
