from fastapi import APIRouter, Request, Form, Response, HTTPException
from fastapi.responses import RedirectResponse
from app.db.database import supabase
from app.api.deps import get_authenticated_user_id
from app.core.config import templates
from app.core.limiter import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/register")
def register_page(request: Request):
    if get_authenticated_user_id(request):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="register.html", context={"request": request, "error": ""})

@router.post("/register")
@limiter.limit("5/minute")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        return templates.TemplateResponse(request=request, name="register.html", context={"request": request, "error": "Passwords do not match."}, status_code=400)
    
    try:
        # Supabase uses email/password for registration
        auth_response = supabase.auth.sign_up({"email": username, "password": password})
        
        # User is created, now seed categories using their ID
        user_id = auth_response.user.id
        supabase.table("users").insert({"id": user_id, "username": username}).execute()
        
    except Exception as e:
        logger.exception(f"Registration failed: {e}")
        return templates.TemplateResponse(request=request, name="register.html", context={"request": request, "error": "Registration failed."}, status_code=400)
        
    return RedirectResponse(url="/login", status_code=303)

@router.get("/login")
def login_page(request: Request, next: str = "/dashboard"):
    if get_authenticated_user_id(request):
        return RedirectResponse(url=next, status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "next_url": next, "error": ""})

@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next_url: str = Form("/dashboard"),
):
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": username, "password": password})
        token = auth_response.session.access_token
        
        response = RedirectResponse(url=next_url, status_code=303)
        response.set_cookie("supabase_auth_token", token, httponly=True, samesite="lax")
        return response
    except Exception:
        return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "next_url": next_url, "error": "Invalid credentials."}, status_code=401)

@router.post("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("supabase_auth_token")
    return response

