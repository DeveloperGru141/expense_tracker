from fastapi import APIRouter, Request, Form, Response, HTTPException
from fastapi.responses import RedirectResponse
from app.core.security import get_password_hash, verify_password, sign_value, get_csrf_token, require_csrf, set_csrf_cookie
from app.core.config import AUTH_COOKIE
from app.db.database import get_connection
from app.api.deps import get_authenticated_user_id
from app.core.config import templates
import sqlite3

router = APIRouter()

def seed_default_categories(user_id: int) -> None:
    defaults = [
        ("Food & Drinks", "#ef4444", 0),
        ("Transport", "#3b82f6", 0),
        ("Bills", "#f59e0b", 0),
        ("Shopping", "#ec4899", 0),
        ("Entertainment", "#8b5cf6", 0),
        ("Health", "#10b981", 0),
    ]
    with get_connection() as connection:
        connection.executemany(
            "INSERT OR IGNORE INTO categories (user_id, name, color, budget_limit) VALUES (?, ?, ?, ?)",
            [(user_id, name, color, budget) for name, color, budget in defaults],
        )
        connection.commit()

@router.get("/register")
def register_page(request: Request):
    if get_authenticated_user_id(request):
        return RedirectResponse(url="/dashboard", status_code=303)
    csrf_token = get_csrf_token(request)
    response = templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request, "csrf_token": csrf_token, "error": ""},
    )
    set_csrf_cookie(response, csrf_token)
    return response

from app.core.limiter import limiter

import logging
logger = logging.getLogger(__name__)

# ... (router definition)

@router.post("/register")
@limiter.limit("5/minute")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
):
    require_csrf(request, csrf_token)
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "csrf_token": csrf_token, "error": "Passwords do not match."},
            status_code=400,
        )
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username.strip(), get_password_hash(password)),
            )
            user_id = cursor.lastrowid
            connection.commit()
            
        logger.info(f"User registered successfully: {username}, ID: {user_id}")
        seed_default_categories(user_id)
        
    except sqlite3.IntegrityError:
        logger.warning(f"Registration failed: Username already exists: {username}")
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "csrf_token": csrf_token, "error": "Username already exists."},
            status_code=400,
        )
    except Exception as e:
        logger.exception(f"Unexpected error during registration for user {username}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(AUTH_COOKIE, sign_value(str(user_id)), httponly=True, samesite="lax")
    set_csrf_cookie(response, csrf_token)
    return response

@router.get("/login")
def login_page(request: Request, next: str = "/dashboard"):
    if get_authenticated_user_id(request):
        return RedirectResponse(url=next, status_code=303)
    csrf_token = get_csrf_token(request)
    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "csrf_token": csrf_token, "next_url": next, "error": ""},
    )
    set_csrf_cookie(response, csrf_token)
    return response

@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next_url: str = Form("/dashboard"),
    csrf_token: str = Form(...),
):
    require_csrf(request, csrf_token)
    with get_connection() as connection:
        user = connection.execute("SELECT id, password_hash FROM users WHERE username = ?", (username.strip(),)).fetchone()
    if user and verify_password(password, user["password_hash"]):
        response = RedirectResponse(url=next_url, status_code=303)
        response.set_cookie(AUTH_COOKIE, sign_value(str(user["id"])), httponly=True, samesite="lax")
        set_csrf_cookie(response, csrf_token)
        return response
    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "csrf_token": csrf_token, "next_url": next_url, "error": "Invalid username or password."},
        status_code=401,
    )
    set_csrf_cookie(response, csrf_token)
    return response

@router.post("/logout")
def logout(request: Request, csrf_token: str = Form(...)):
    require_csrf(request, csrf_token)
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(AUTH_COOKIE)
    return response
