import os
import threading
from typing import Any
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(url, key)

_local = threading.local()

# Set the auth token for the current thread's Supabase client.
def set_auth(token: str):
    _local.token = token
    supabase.postgrest.auth(token)

# Return the Supabase client, applying thread-local auth if set.
def get_supabase() -> Any:
    token = getattr(_local, "token", None)
    if token:
        supabase.postgrest.auth(token)
    return supabase
