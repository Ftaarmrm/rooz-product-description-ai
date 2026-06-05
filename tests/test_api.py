"""
Test suite for Rooz Product Description AI API.
All Groq calls are mocked — no real API key required.
"""

import pytest

GENERATE_URL = "/v1/product-description/generate"

BASE_REQUEST = {
    "product_name": "Wireless Gaming Mouse",
    "features": ["RGB lighting", "Rechargeable battery", "Low latency"],
    "language": "en",
    "tone": "persuasive",
    "platform": "shopify",
    "target_audience": "gamers",
}


# ── Public endpoints ─────────────────────────────────────────────────────────

def test_health_no_secret(client):
    """GET /health returns 200 without any auth."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "Rooz" in data["service"]


def test_landing_page_no_secret(client):
    """GET / returns landing page HTML without any auth."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


def test_openapi_no_secret(client):
    """GET /openapi.json returns 200 without any auth."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "openapi" in data


# ── Auth / middleware ─────────────────────────────────────────────────────────

def test_generate_production_no_secret_returns_403(client_production_no_secret):
    """POST generate in production with no RAPIDAPI_PROXY_SECRET → 403 (Fail Closed)."""
    resp = client_production_no_secret.post(GENERATE_URL, json=BASE_REQUEST)
    assert resp.status_code == 403


def test_generate_with_correct_secret_returns_200(client_with_secret):
    """POST generate with correct X-RapidAPI-Proxy-Secret → 200."""
    resp = client_with_secret.post(
        GENERATE_URL,
        json=BASE_REQUEST,
        headers={"X-RapidAPI-Proxy-Secret": "test-secret-abc"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["product_name"] == "Wireless Gaming Mouse"
    assert "short_description" in data
    assert "long_description" in data
    assert isinstance(data["bullet_points"], list)
    assert "seo_title" in data
    assert "meta_description" in data


def test_generate_wrong_secret_returns_403(client_with_secret):
    """POST generate with wrong proxy secret → 403."""
    resp = client_with_secret.post(
        GENERATE_URL,
        json=BASE_REQUEST,
        headers={"X-RapidAPI-Proxy-Secret": "wrong-secret"},
    )
    assert resp.status_code == 403


# ── Validation ────────────────────────────────────────────────────────────────

def test_empty_product_name_returns_422(client):
    """product_name with only whitespace → 422."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "product_name": "   "})
    assert resp.status_code == 422


def test_blank_product_name_returns_422(client):
    """Empty product_name string → 422."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "product_name": ""})
    assert resp.status_code == 422


def test_unsupported_language_returns_422(client):
    """language='de' (German, not supported) → 422."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "language": "de"})
    assert resp.status_code == 422


def test_invalid_platform_returns_422(client):
    """platform='ebay' (not in allowed list) → 422."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "platform": "ebay"})
    assert resp.status_code == 422


def test_invalid_tone_returns_422(client):
    """tone='aggressive' (not in allowed list) → 422."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "tone": "aggressive"})
    assert resp.status_code == 422


# ── Language support ──────────────────────────────────────────────────────────

def test_english_request(client):
    """language='en' → 200 with expected fields."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "language": "en"})
    assert resp.status_code == 200
    assert resp.json()["language"] == "en"


def test_arabic_request(client):
    """language='ar' → 200 with expected fields."""
    resp = client.post(
        GENERATE_URL,
        json={**BASE_REQUEST, "language": "ar", "arabic_style": "formal"},
    )
    assert resp.status_code == 200
    assert resp.json()["language"] == "ar"


def test_spanish_request(client):
    """language='es' → 200 with expected fields."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "language": "es"})
    assert resp.status_code == 200
    assert resp.json()["language"] == "es"


def test_hindi_request(client):
    """language='hi' → 200 with expected fields."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "language": "hi"})
    assert resp.status_code == 200
    assert resp.json()["language"] == "hi"


def test_french_request(client):
    """language='fr' → 200 with expected fields."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "language": "fr"})
    assert resp.status_code == 200
    assert resp.json()["language"] == "fr"


def test_unsupported_language_de_returns_422(client):
    """language='de' → 422 (German not supported)."""
    resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "language": "de"})
    assert resp.status_code == 422


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_minimal_request(client):
    """Only product_name provided — all optional fields use defaults."""
    resp = client.post(GENERATE_URL, json={"product_name": "Smart Watch"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["language"] == "en"
    assert data["tone"] == "professional"
    assert data["platform"] == "general"


def test_response_structure(client):
    """Response contains all required fields."""
    resp = client.post(GENERATE_URL, json=BASE_REQUEST)
    assert resp.status_code == 200
    data = resp.json()
    required = {
        "product_name", "short_description", "long_description",
        "bullet_points", "seo_title", "meta_description",
        "language", "tone", "platform",
    }
    assert required.issubset(set(data.keys()))
    assert isinstance(data["bullet_points"], list)
    assert len(data["bullet_points"]) >= 1


def test_arabic_style_ignored_for_non_arabic(client):
    """arabic_style field should be accepted but not affect non-Arabic results."""
    resp = client.post(
        GENERATE_URL,
        json={**BASE_REQUEST, "language": "en", "arabic_style": "saudi_white"},
    )
    assert resp.status_code == 200


def test_all_platforms_accepted(client):
    """All allowed platforms return 200."""
    platforms = ["general", "shopify", "woocommerce", "salla", "zid", "amazon", "noon", "aliexpress"]
    for platform in platforms:
        resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "platform": platform})
        assert resp.status_code == 200, f"Platform '{platform}' failed with {resp.status_code}"


def test_all_tones_accepted(client):
    """All allowed tones return 200."""
    tones = ["professional", "persuasive", "luxury", "simple"]
    for tone in tones:
        resp = client.post(GENERATE_URL, json={**BASE_REQUEST, "tone": tone})
        assert resp.status_code == 200, f"Tone '{tone}' failed with {resp.status_code}"


# ── Provider fallback (Groq → OpenRouter) ─────────────────────────────────────

def test_fallback_used_when_groq_fails(client_with_secret, monkeypatch):
    """If Groq fails and OpenRouter is configured, the fallback is used → 200."""
    import os
    os.environ["OPENROUTER_API_KEY"] = "test-openrouter-key"
    from app.config import get_settings
    get_settings.cache_clear()

    import app.services.groq_service as svc

    async def _boom(prompt, settings):
        raise RuntimeError("groq down")

    async def _fallback_ok(prompt, settings):
        import json
        return json.dumps({
            "short_description": "From OpenRouter fallback.",
            "long_description": "This came from the OpenRouter fallback provider.",
            "bullet_points": ["Point A", "Point B", "Point C"],
            "seo_title": "Fallback SEO Title",
            "meta_description": "Fallback meta description for the product.",
        })

    monkeypatch.setattr(svc, "_call_groq", _boom)
    monkeypatch.setattr(svc, "_call_openrouter", _fallback_ok)

    resp = client_with_secret.post(
        GENERATE_URL,
        json=BASE_REQUEST,
        headers={"X-RapidAPI-Proxy-Secret": "test-secret-abc"},
    )
    os.environ.pop("OPENROUTER_API_KEY", None)
    get_settings.cache_clear()

    assert resp.status_code == 200
    assert resp.json()["short_description"] == "From OpenRouter fallback."


def test_error_when_both_providers_fail(client_with_secret, monkeypatch):
    """If Groq fails and OpenRouter also fails, client gets a 503 (no leak)."""
    import os
    os.environ["OPENROUTER_API_KEY"] = "test-openrouter-key"
    from app.config import get_settings
    get_settings.cache_clear()

    import app.services.groq_service as svc

    async def _boom(prompt, settings):
        raise RuntimeError("provider down")

    monkeypatch.setattr(svc, "_call_groq", _boom)
    monkeypatch.setattr(svc, "_call_openrouter", _boom)

    resp = client_with_secret.post(
        GENERATE_URL,
        json=BASE_REQUEST,
        headers={"X-RapidAPI-Proxy-Secret": "test-secret-abc"},
    )
    os.environ.pop("OPENROUTER_API_KEY", None)
    get_settings.cache_clear()

    assert resp.status_code == 503
    # Ensure the raw internal error text is NOT exposed to the client
    assert "provider down" not in resp.text
