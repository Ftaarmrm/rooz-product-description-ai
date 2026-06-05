from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """Public health check endpoint — no authentication required."""
    return HealthResponse(
        status="ok",
        service="Rooz Product Description AI",
        version="1.0.0",
    )
