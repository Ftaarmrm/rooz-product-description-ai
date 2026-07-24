import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.middleware.rapidapi import RapidAPIProxySecretMiddleware
from app.routers import health, product_description

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Rooz Product Description AI | env=%s", settings.APP_ENV)
    if settings.is_production and not settings.RAPIDAPI_PROXY_SECRET:
        logger.critical(
            "RAPIDAPI_PROXY_SECRET is not set in production! "
            "All commercial endpoints will be rejected (Fail Closed)."
        )
    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY is not set. AI calls will fail.")
    yield
    logger.info("Shutting down Rooz Product Description AI.")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Rooz Product Description AI",
    description=(
        "Generate AI-powered product descriptions for e-commerce platforms in 5 languages: "
        "English, Arabic, Spanish, Hindi, and French."
    ),
    version="1.0.0",
    license_info={"name": "Proprietary — All Rights Reserved"},
    lifespan=lifespan,
    root_path=settings.ROOT_PATH,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# RapidAPI Proxy Secret Middleware
# ---------------------------------------------------------------------------
app.add_middleware(RapidAPIProxySecretMiddleware)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health.router)
app.include_router(product_description.router)

# ---------------------------------------------------------------------------
# Static files / Landing page
# ---------------------------------------------------------------------------
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", include_in_schema=False)
async def landing_page():
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"service": "Rooz Product Description AI", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Favicon routes
# ---------------------------------------------------------------------------
@app.get("/favicon.ico", include_in_schema=False)
async def favicon_ico():
    icon_path = static_dir / "favicon.ico"
    if icon_path.exists():
        return FileResponse(str(icon_path))
    return Response(status_code=204)


@app.get("/favicon.png", include_in_schema=False)
async def favicon_png():
    icon_path = static_dir / "favicon.png"
    if icon_path.exists():
        return FileResponse(str(icon_path))
    return Response(status_code=204)
