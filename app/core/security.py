import hashlib
import hmac
import secrets
import bcrypt
from fastapi import Request, HTTPException
from app.core.config import SESSION_SECRET, AUTH_COOKIE, CSRF_COOKIE

def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def sign_value(value: str) -> str:
    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{value}.{signature}"

def verify_signed_value(signed_value: str | None) -> str | None:
    if not signed_value or "." not in signed_value:
        return None
    value, signature = signed_value.rsplit(".", 1)
    expected = sign_value(value).rsplit(".", 1)[1]
    if hmac.compare_digest(signature, expected):
        return value
    return None

def get_csrf_token(request: Request) -> str:
    return request.cookies.get(CSRF_COOKIE) or secrets.token_urlsafe(32)

def require_csrf(request: Request, csrf_token: str) -> None:
    expected_token = request.cookies.get(CSRF_COOKIE)
    if not expected_token or csrf_token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")

def set_csrf_cookie(response, csrf_token: str, is_secure: bool = False) -> None:
    response.set_cookie(
        CSRF_COOKIE,
        csrf_token,
        httponly=True,
        samesite="lax",
        secure=is_secure,
    )
