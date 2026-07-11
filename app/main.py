import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import logging
import sys

from app.core.config import BASE_DIR, templates
from app.core.security import get_csrf_token, set_csrf_cookie
from app.api.endpoints import auth, expenses, income, analytics, settings, recurring
from app.core.limiter import limiter
from app.db.database import get_supabase
from app.exceptions import AppError, DatabaseError, AuthError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

CORS_ORIGINS = [o for o in os.getenv("CORS_ORIGINS", "").split(",") if o] or ["http://localhost:8000"]

# Application lifespan handler for startup/shutdown events.
@asynccontextmanager
async def lifespan(_: FastAPI):
    yield

app = FastAPI(title="Expense Tracker", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Handle database errors with a 500 response.
@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "A database error occurred."})

# Redirect unauthenticated users to login.
@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    return RedirectResponse(url="/login", status_code=303)

# Handle generic application errors with a 500 response.
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.error(f"Application error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "An internal error occurred."})

# Catch-all handler for unhandled exceptions.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

# Health check endpoint returning service and database status.
@app.get("/health")
def health_check():
    db_ok = False
    try:
        get_supabase().table("users").select("id").limit(1).execute()
        db_ok = True
    except Exception:
        pass
    return {"status": "healthy" if db_ok else "degraded", "database": "connected" if db_ok else "unreachable", "service": "expense-tracker"}

# Serve the favicon image.
@app.get("/favicon.ico")
def favicon():
    return FileResponse(BASE_DIR / "static" / "images" / "calculator.png", media_type="image/png")

# Serve the service worker JavaScript file.
@app.get("/sw.js")
def service_worker():
    return FileResponse(BASE_DIR / "static" / "sw.js", media_type="application/javascript")

# Render the landing page with CSRF protection.
@app.get("/")
@limiter.limit("20/minute")
def landing_page(request: Request):
    csrf_token = get_csrf_token(request)
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "csrf_token": csrf_token},
    )
    is_secure = request.url.scheme == "https"
    set_csrf_cookie(response, csrf_token, is_secure=is_secure)
    return response

app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(income.router)
app.include_router(analytics.router)
app.include_router(settings.router)
app.include_router(recurring.router)
