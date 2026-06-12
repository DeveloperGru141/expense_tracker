from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import BASE_DIR, templates
from app.core.security import get_csrf_token, set_csrf_cookie
from app.api.endpoints import auth, expenses, income, analytics, settings, recurring
from app.core.limiter import limiter

@asynccontextmanager
async def lifespan(_: FastAPI):
    yield

app = FastAPI(title="Expense Tracker", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/sw.js")
def service_worker(request: Request):
    return FileResponse(BASE_DIR / "static" / "sw.js", media_type="application/javascript")

@app.get("/")
@limiter.limit("20/minute")
def landing_page(request: Request):
    csrf_token = get_csrf_token(request)
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "csrf_token": csrf_token},
    )
    set_csrf_cookie(response, csrf_token)
    return response

# Include Routers
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(income.router)
app.include_router(analytics.router)
app.include_router(settings.router)
app.include_router(recurring.router)
