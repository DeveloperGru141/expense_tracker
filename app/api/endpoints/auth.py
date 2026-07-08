from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.db.database import supabase
from app.api.deps import get_authenticated_user_id
from app.core.config import templates
from app.core.limiter import limiter
from app.core.security import get_csrf_token, set_csrf_cookie, require_csrf
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_EMAIL_LENGTH = 254
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Show the registration page.
@router.get("/register")
def register_page(request: Request):
    if get_authenticated_user_id(request):
        return RedirectResponse(url="/dashboard", status_code=303)

    csrf_token = get_csrf_token(request)
    response = templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request, "error": "", "csrf_token": csrf_token},
    )
    is_secure = request.url.scheme == "https"
    set_csrf_cookie(response, csrf_token, is_secure=is_secure)
    return response

# Handle user registration form submission.
@router.post("/register")
@limiter.limit("5/minute")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
):
    require_csrf(request, csrf_token)
    email = email.strip().lower()[:MAX_EMAIL_LENGTH]
    password = password[:MAX_PASSWORD_LENGTH]

    if not email or "@" not in email:
        csrf_token = get_csrf_token(request)
        response = templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "error": "Invalid email address.", "csrf_token": csrf_token, "email": email},
            status_code=400,
        )
        is_secure = request.url.scheme == "https"
        set_csrf_cookie(response, csrf_token, is_secure=is_secure)
        return response

    if len(password) < MIN_PASSWORD_LENGTH:
        csrf_token = get_csrf_token(request)
        response = templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "error": f"Password must be at least {MIN_PASSWORD_LENGTH} characters.", "csrf_token": csrf_token, "email": email},
            status_code=400,
        )
        is_secure = request.url.scheme == "https"
        set_csrf_cookie(response, csrf_token, is_secure=is_secure)
        return response

    if password != confirm_password:
        csrf_token = get_csrf_token(request)
        response = templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "error": "Passwords do not match.", "csrf_token": csrf_token, "email": email},
            status_code=400,
        )
        is_secure = request.url.scheme == "https"
        set_csrf_cookie(response, csrf_token, is_secure=is_secure)
        return response

    try:
        try:
            auth_response = supabase.auth.sign_up({"email": email, "password": password})
        except Exception as e:
            logger.error(f"Supabase Auth sign_up failed: {e}")
            error_msg = str(e)
            if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
                error_msg = "An account with this email already exists."
            csrf_token = get_csrf_token(request)
            response = templates.TemplateResponse(
                request=request,
                name="register.html",
                context={"request": request, "error": f"Registration failed: {error_msg}", "csrf_token": csrf_token, "email": email},
                status_code=400,
            )
            is_secure = request.url.scheme == "https"
            set_csrf_cookie(response, csrf_token, is_secure=is_secure)
            return response

        if not auth_response or not auth_response.user:
            csrf_token = get_csrf_token(request)
            response = templates.TemplateResponse(
                request=request,
                name="register.html",
                context={"request": request, "error": "Registration failed: No user returned.", "csrf_token": csrf_token, "email": email},
                status_code=400,
            )
            is_secure = request.url.scheme == "https"
            set_csrf_cookie(response, csrf_token, is_secure=is_secure)
            return response

    except Exception as e:
        logger.error(f"Registration failed: {e}")
        csrf_token = get_csrf_token(request)
        response = templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "error": "Registration failed. Please try again.", "csrf_token": csrf_token, "email": email},
            status_code=400,
        )
        is_secure = request.url.scheme == "https"
        set_csrf_cookie(response, csrf_token, is_secure=is_secure)
        return response

    return RedirectResponse(url="/login?registered=1", status_code=303)

# Show the login page.
@router.get("/login")
def login_page(request: Request, next: str = "/dashboard", registered: int = 0):
    if get_authenticated_user_id(request):
        return RedirectResponse(url=next, status_code=303)

    msg = "Registration successful! Please sign in." if registered else ""

    csrf_token = get_csrf_token(request)
    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "next_url": next, "error": "", "info": msg, "csrf_token": csrf_token},
    )
    is_secure = request.url.scheme == "https"
    set_csrf_cookie(response, csrf_token, is_secure=is_secure)
    return response

# Handle login form submission and set auth cookie.
@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    next_url: str = Form("/dashboard"),
):
    require_csrf(request, csrf_token)
    email = email.strip().lower()[:MAX_EMAIL_LENGTH]
    password = password[:MAX_PASSWORD_LENGTH]

    if not email or not password:
        csrf_token = get_csrf_token(request)
        response = templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"request": request, "next_url": next_url, "error": "Email and password are required.", "csrf_token": csrf_token, "email": email},
        )
        is_secure = request.url.scheme == "https"
        set_csrf_cookie(response, csrf_token, is_secure=is_secure)
        return response

    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})

        if not auth_response or not auth_response.session:
            csrf_token = get_csrf_token(request)
            response = templates.TemplateResponse(
                request=request,
                name="login.html",
                context={"request": request, "next_url": next_url, "error": "Invalid email or password.", "csrf_token": csrf_token, "email": email},
            )
            is_secure = request.url.scheme == "https"
            set_csrf_cookie(response, csrf_token, is_secure=is_secure)
            return response

        token = auth_response.session.access_token

        response = RedirectResponse(url=next_url, status_code=303)
        is_secure = request.url.scheme == "https"
        response.set_cookie(
            "supabase_auth_token",
            token,
            httponly=True,
            samesite="lax",
            secure=is_secure,
        )
        return response
    except Exception as e:
        logger.warning(f"Login attempt failed for {email}: {e}")
        csrf_token = get_csrf_token(request)
        response = templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"request": request, "next_url": next_url, "error": "Invalid email or password.", "csrf_token": csrf_token, "email": email},
        )
        is_secure = request.url.scheme == "https"
        set_csrf_cookie(response, csrf_token, is_secure=is_secure)
        return response

# Log out the user by deleting the auth cookie.
@router.post("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("supabase_auth_token")
    return response
