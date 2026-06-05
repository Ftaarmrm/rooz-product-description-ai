import json
import logging
import re
import httpx
from groq import AsyncGroq

from app.config import get_settings
from app.models import ProductDescriptionRequest, ProductDescriptionResponse

logger = logging.getLogger(__name__)

LANGUAGE_INSTRUCTIONS = {
    "en": "Write in professional marketing English suitable for e-commerce.",
    "ar": "اكتب بلغة عربية واضحة مناسبة للتجارة الإلكترونية.",
    "es": (
        "Escribe en español profesional adecuado para el comercio electrónico. "
        "Usa un estilo de marketing claro y apropiado para tiendas en línea."
    ),
    "hi": (
        "हिंदी भाषा में लिखें। ई-कॉमर्स के लिए स्पष्ट और उचित शैली का उपयोग करें। "
        "Hinglish का उपयोग न करें।"
    ),
    "fr": (
        "Écris en français professionnel adapté au commerce électronique. "
        "Utilise un style marketing clair et approprié pour les boutiques en ligne."
    ),
}

ARABIC_STYLE_INSTRUCTIONS = {
    "formal": "استخدم عربية فصحى مبسطة.",
    "saudi_white": "استخدم لهجة سعودية بيضاء خفيفة وواضحة بدون مبالغة.",
    "gulf_commercial": "استخدم أسلوبًا تجاريًا خليجيًا واضحًا ومناسبًا للمتاجر.",
}


def _build_prompt(req: ProductDescriptionRequest) -> str:
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(req.language, LANGUAGE_INSTRUCTIONS["en"])

    if req.language == "ar":
        arabic_instruction = ARABIC_STYLE_INSTRUCTIONS.get(req.arabic_style, "")
        lang_instruction = f"{lang_instruction}\n{arabic_instruction}"

    features_text = ""
    if req.features:
        features_text = "\nProduct features:\n" + "\n".join(f"- {f}" for f in req.features)

    audience_text = ""
    if req.target_audience:
        audience_text = f"\nTarget audience: {req.target_audience}"

    prompt = f"""You are a professional e-commerce copywriter. Generate a product description for the following product.

{lang_instruction}

Product name: {req.product_name}
Tone: {req.tone}
Platform: {req.platform}{features_text}{audience_text}

Rules:
- Do NOT translate brand names or model names.
- Do NOT invent features not listed above.
- Do NOT make medical, legal, or unverified guarantee claims.
- Do NOT write Markdown formatting.
- Write all content in the same language specified by the language instruction above.
- seo_title must not exceed 70 characters.
- meta_description must not exceed 160 characters.
- bullet_points must be between 3 and 5 items.

Respond ONLY with a valid JSON object — no preamble, no explanation, no markdown code blocks.

JSON structure:
{{
  "short_description": "...",
  "long_description": "...",
  "bullet_points": ["...", "...", "..."],
  "seo_title": "...",
  "meta_description": "..."
}}"""
    return prompt


def _extract_json(text: str) -> dict:
    """Extract JSON from response text, handling potential non-JSON wrapping."""
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON block from markdown code fences
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find first { ... } block
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from Groq response: {text[:300]}")


async def _call_groq(prompt: str, settings) -> str:
    """Call Groq. Returns raw text content. Raises on any failure."""
    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    completion = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500,
        response_format={"type": "json_object"},
        timeout=30.0,
    )
    return completion.choices[0].message.content or ""


async def _call_openrouter(prompt: str, settings) -> str:
    """Call OpenRouter (OpenAI-compatible). Returns raw text content. Raises on failure."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1500,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        body = resp.json()
        return body["choices"][0]["message"]["content"] or ""


async def _get_ai_response(prompt: str, settings) -> str:
    """
    Get a raw AI response using Groq as the primary provider.
    If Groq fails AND OpenRouter is configured, automatically fall back to it.
    Raises RuntimeError (with a generic, client-safe message) only if all
    available providers fail.
    """
    # Primary: Groq
    try:
        return await _call_groq(prompt, settings)
    except Exception as exc:
        logger.error("Groq call failed: %s", exc)
        if not settings.openrouter_enabled:
            raise RuntimeError(
                "AI service is temporarily unavailable. Please try again."
            ) from exc

    # Fallback: OpenRouter
    logger.warning("Falling back to OpenRouter after Groq failure.")
    try:
        return await _call_openrouter(prompt, settings)
    except Exception as exc:
        logger.error("OpenRouter fallback also failed: %s", exc)
        raise RuntimeError(
            "AI service is temporarily unavailable. Please try again."
        ) from exc


async def generate_product_description(
    req: ProductDescriptionRequest,
) -> ProductDescriptionResponse:
    settings = get_settings()
    prompt = _build_prompt(req)

    logger.info(
        "Generating | groq_model=%s | fallback=%s | language=%s | tone=%s | platform=%s",
        settings.GROQ_MODEL,
        "openrouter" if settings.openrouter_enabled else "none",
        req.language,
        req.tone,
        req.platform,
    )

    raw = await _get_ai_response(prompt, settings)
    logger.debug("AI raw response: %s", raw[:500])

    try:
        data = _extract_json(raw)
    except ValueError as exc:
        logger.error("JSON extraction failed: %s", exc)
        raise ValueError("AI returned an invalid response. Please try again.") from exc

    # Validate required keys
    required_keys = {
        "short_description", "long_description", "bullet_points", "seo_title", "meta_description"
    }
    missing = required_keys - set(data.keys())
    if missing:
        raise ValueError(f"AI response missing fields: {missing}")

    # Normalize bullet_points: must be a non-empty list of strings, capped at 5.
    bullets = data["bullet_points"]
    if not isinstance(bullets, list):
        raise ValueError("AI response 'bullet_points' is not a list.")
    bullets = [str(b).strip() for b in bullets if str(b).strip()]
    if not bullets:
        raise ValueError("AI response returned no usable bullet points.")
    # Spec requires 3–5 bullet points. Trim extras; if fewer than 3 we keep what
    # we have rather than fail, since the rest of the description is still valid.
    bullets = bullets[:5]

    return ProductDescriptionResponse(
        product_name=req.product_name,
        short_description=str(data["short_description"]).strip(),
        long_description=str(data["long_description"]).strip(),
        bullet_points=bullets,
        seo_title=str(data["seo_title"]).strip(),
        meta_description=str(data["meta_description"]).strip(),
        language=req.language,
        tone=req.tone,
        platform=req.platform,
    )
