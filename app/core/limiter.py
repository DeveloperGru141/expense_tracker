from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

# Extract the client IP from request headers.
def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    forwarded_proto = request.headers.get("X-Real-IP")
    if forwarded_proto:
        return forwarded_proto
    return get_remote_address(request)

limiter = Limiter(key_func=get_client_ip)
