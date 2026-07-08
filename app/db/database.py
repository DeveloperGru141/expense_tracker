import os
from contextvars import ContextVar
from typing import Any
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(url, key)

_auth_token: ContextVar[str | None] = ContextVar("auth_token", default=None)


def set_auth(token: str):
    _auth_token.set(token)
    supabase.postgrest.auth(token)


def get_supabase() -> Any:
    token = _auth_token.get()
    if token:
        supabase.postgrest.auth(token)
    return supabase
