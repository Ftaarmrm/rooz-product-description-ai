import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings

logger = logging.getLogger(__name__)

PUBLIC_PATHS = {
    "/",
    "/health",
    "/openapi.json",
    "/docs",
    "/redoc",
    "/docs/oauth2-redirect",
}


class RapidAPIProxySecretMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow public paths without any auth check
        if path in PUBLIC_PATHS or path.startswith("/static/"):
            return await call_next(request)

        settings = get_settings()
        secret = settings.RAPIDAPI_PROXY_SECRET

        # Fail Closed: production with no secret configured → reject all commercial routes
        if settings.is_production and not secret:
            logger.error(
                "RAPIDAPI_PROXY_SECRET is not configured in production. "
                "Rejecting request to %s", path
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "Service is not properly configured. Contact support."},
            )

        # Dev/Test with no secret configured → allow through for development convenience
        if settings.is_dev_or_test and not secret:
            logger.warning(
                "RAPIDAPI_PROXY_SECRET not set. Allowing request in %s mode.", settings.APP_ENV
            )
            return await call_next(request)

        # Validate the proxy secret header
        incoming_secret = request.headers.get("X-RapidAPI-Proxy-Secret", "")
        if not incoming_secret:
            logger.warning("Missing X-RapidAPI-Proxy-Secret header for path %s", path)
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden: missing authentication."},
            )

        if incoming_secret != secret:
            logger.warning("Invalid X-RapidAPI-Proxy-Secret for path %s", path)
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden: invalid authentication."},
            )

        return await call_next(request)
