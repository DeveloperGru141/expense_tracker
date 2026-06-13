from fastapi import APIRouter, Request, Form
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
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request, 
            name="register.html", 
            context={"request": request, "error": "Passwords do not match."}, 
            status_code=400
        )
    
    try:
        # 1. Sign up user in Supabase Auth
        try:
            auth_response = supabase.auth.sign_up({"email": email, "password": password})
        except Exception as e:
            logger.error(f"Supabase Auth sign_up failed: {e}")
            return templates.TemplateResponse(
                request=request, 
                name="register.html", 
                context={"request": request, "error": "Registration failed. User may already exist."}, 
                status_code=400
            )

        if not auth_response.user:
            return templates.TemplateResponse(
                request=request, 
                name="register.html", 
                context={"request": request, "error": "Registration failed: No user returned."}, 
                status_code=400
            )

    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return templates.TemplateResponse(
            request=request, 
            name="register.html", 
            context={"request": request, "error": "Registration failed. Please try again."}, 
            status_code=400
        )
        
    return RedirectResponse(url="/login?registered=1", status_code=303)

@router.get("/login")
def login_page(request: Request, next: str = "/dashboard", registered: int = 0):
    if get_authenticated_user_id(request):
        return RedirectResponse(url=next, status_code=303)
    
    msg = "Registration successful! Please sign in." if registered else ""
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={"request": request, "next_url": next, "error": "", "info": msg}
    )

@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next_url: str = Form("/dashboard"),
):
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        if not auth_response.session:
            raise Exception("No session returned")

        token = auth_response.session.access_token
        
        response = RedirectResponse(url=next_url, status_code=303)
        # Use a more secure cookie configuration
        is_secure = request.url.scheme == "https"
        response.set_cookie(
            "supabase_auth_token", 
            token, 
            httponly=True, 
            samesite="lax",
            secure=is_secure
        )
        return response
    except Exception as e:
        logger.warning(f"Login attempt failed for {email}: {e}")
        return templates.TemplateResponse(
            request=request, 
            name="login.html", 
            context={"request": request, "next_url": next_url, "error": "Invalid email or password."}
        )

@router.post("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("supabase_auth_token")
    return response

 