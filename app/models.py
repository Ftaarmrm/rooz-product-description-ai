from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field, field_validator


SUPPORTED_LANGUAGES = Literal["en", "ar", "es", "hi", "fr"]
SUPPORTED_TONES = Literal["professional", "persuasive", "luxury", "simple"]
SUPPORTED_PLATFORMS = Literal[
    "general", "shopify", "woocommerce", "salla", "zid", "amazon", "noon", "aliexpress"
]
SUPPORTED_ARABIC_STYLES = Literal["formal", "saudi_white", "gulf_commercial"]


class ProductDescriptionRequest(BaseModel):
    product_name: Annotated[str, Field(min_length=2, max_length=150)]
    features: Annotated[
        Optional[list[Annotated[str, Field(max_length=120)]]],
        Field(default=None, max_length=10),
    ] = None
    language: SUPPORTED_LANGUAGES = "en"
    tone: SUPPORTED_TONES = "professional"
    platform: SUPPORTED_PLATFORMS = "general"
    target_audience: Annotated[Optional[str], Field(default=None, max_length=120)] = None
    arabic_style: SUPPORTED_ARABIC_STYLES = "formal"

    @field_validator("product_name")
    @classmethod
    def product_name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("product_name must not be empty or whitespace only")
        return v.strip()


class ProductDescriptionResponse(BaseModel):
    product_name: str
    short_description: str
    long_description: str
    bullet_points: list[str]
    seo_title: str
    meta_description: str
    language: str
    tone: str
    platform: str
