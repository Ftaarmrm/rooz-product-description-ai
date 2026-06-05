import logging
from fastapi import APIRouter, HTTPException
from app.models import ProductDescriptionRequest, ProductDescriptionResponse
from app.services.groq_service import generate_product_description

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/product-description", tags=["Product Description"])


@router.post(
    "/generate",
    response_model=ProductDescriptionResponse,
    summary="Generate AI product description",
    description=(
        "Generate a professional product description for e-commerce platforms. "
        "Supports 5 languages: English (en), Arabic (ar), Spanish (es), Hindi (hi), French (fr)."
    ),
)
async def generate_description(
    request: ProductDescriptionRequest,
) -> ProductDescriptionResponse:
    """
    Generate AI-powered product descriptions including:
    - Short description (product card)
    - Long description (product page)
    - Bullet points (3–5 key features)
    - SEO title (≤70 chars)
    - Meta description (≤160 chars)
    """
    logger.info(
        "Generate request | product=%s | lang=%s | tone=%s | platform=%s",
        request.product_name,
        request.language,
        request.tone,
        request.platform,
    )

    try:
        result = await generate_product_description(request)
    except ValueError as exc:
        logger.error("Generation failed (ValueError): %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    except RuntimeError as exc:
        logger.error("Generation failed (RuntimeError): %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error during generation")
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    return result
