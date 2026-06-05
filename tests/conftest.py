import os
import sys
import types
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Groq stub — must be injected into sys.modules BEFORE any app code is
# imported.  This makes `from groq import AsyncGroq` succeed even when the
# real `groq` package is not installed in the test environment.
# The stub is replaced by a proper AsyncMock inside the mock_groq fixture.
# ---------------------------------------------------------------------------
def _install_groq_stub() -> None:
    if "groq" not in sys.modules:
        groq_stub = types.ModuleType("groq")

        class AsyncGroqStub:
            def __init__(self, *args, **kwargs):
                pass

        groq_stub.AsyncGroq = AsyncGroqStub  # type: ignore[attr-defined]
        sys.modules["groq"] = groq_stub


_install_groq_stub()

# TestClient can now be imported safely (it pulls in FastAPI which in turn
# may trigger app imports that reference groq).
from fastapi.testclient import TestClient  # noqa: E402


def pytest_configure(config):
    """Set environment variables before any app code is imported."""
    os.environ.setdefault("APP_ENV", "test")
    os.environ.setdefault("GROQ_API_KEY", "test-key-not-real")
    os.environ.setdefault("GROQ_MODEL", "llama-3.3-70b-versatile")
    os.environ.setdefault("LOG_LEVEL", "WARNING")
    # RAPIDAPI_PROXY_SECRET intentionally left unset for dev/test bypass testing.
    # Individual tests that need it will set it themselves.


MOCK_GROQ_RESPONSE = {
    "short_description": "High-quality product for discerning customers.",
    "long_description": "This premium product delivers outstanding performance and value.",
    "bullet_points": [
        "Top feature one",
        "Top feature two",
        "Top feature three",
    ],
    "seo_title": "Best Product - Top Quality",
    "meta_description": "Shop the best product with premium quality and great value for money.",
}


def _make_mock_completion(content: dict | None = None):
    """Build a mock Groq completion object."""
    data = content or MOCK_GROQ_RESPONSE
    message = MagicMock()
    message.content = json.dumps(data)
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]
    return completion


@pytest.fixture
def mock_groq():
    """Patch AsyncGroq so tests never call the real Groq API."""
    mock_completion = _make_mock_completion()
    with patch("app.services.groq_service.AsyncGroq") as MockGroq:
        instance = AsyncMock()
        instance.chat.completions.create = AsyncMock(return_value=mock_completion)
        MockGroq.return_value = instance
        yield MockGroq


@pytest.fixture
def client(mock_groq):
    """TestClient with Groq mocked and no proxy secret (dev/test mode)."""
    # Ensure no secret is set so middleware is in dev/test bypass mode
    os.environ.pop("RAPIDAPI_PROXY_SECRET", None)

    # Clear the settings cache so new env vars are picked up
    from app.config import get_settings
    get_settings.cache_clear()

    from app.main import app
    with TestClient(app) as c:
        yield c

    get_settings.cache_clear()


@pytest.fixture
def client_with_secret(mock_groq):
    """TestClient with a proxy secret configured."""
    os.environ["APP_ENV"] = "production"
    os.environ["RAPIDAPI_PROXY_SECRET"] = "test-secret-abc"

    from app.config import get_settings
    get_settings.cache_clear()

    from app.main import app
    with TestClient(app) as c:
        yield c

    os.environ["APP_ENV"] = "test"
    os.environ.pop("RAPIDAPI_PROXY_SECRET", None)
    get_settings.cache_clear()


@pytest.fixture
def client_production_no_secret(mock_groq):
    """TestClient in production mode with NO proxy secret (Fail Closed)."""
    os.environ["APP_ENV"] = "production"
    os.environ.pop("RAPIDAPI_PROXY_SECRET", None)

    from app.config import get_settings
    get_settings.cache_clear()

    from app.main import app
    with TestClient(app) as c:
        yield c

    os.environ["APP_ENV"] = "test"
    get_settings.cache_clear()
