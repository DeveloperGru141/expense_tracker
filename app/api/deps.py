import os
from fastapi import Request, HTTPException
from supabase import create_client
from gotrue import AuthApiError

# We need a new Supabase client specifically for Auth if we want to verify tokens,
# or we can verify the JWT locally using pyjwt if we have the secret.
# For simplicity, we use the client to get the user from the token.
from app.db.database import supabase

def get_authenticated_user_id(request: Request) -> str | None:
    token = request.cookies.get("supabase_auth_token")
    if not token:
        return None
    
    try:
        user = supabase.auth.get_user(token)
        return user.user.id
    except Exception:
        return None

def require_user(request: Request) -> str:
    user_id = get_authenticated_user_id(request)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_id
