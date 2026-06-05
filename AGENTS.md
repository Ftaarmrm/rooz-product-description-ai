# Rooz Product Description AI — AI Agent Instructions

> AI-powered multilingual product description API with 5-language support, Groq+OpenRouter fallback, and RapidAPI monetization. Deployed via Coolify, GitHub-sourced.

---

## 📋 Quick Reference

| Command | Purpose |
|---------|---------|
| `pytest tests/ -v` | Run full test suite (mocked Groq, no API key needed) |
| `.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000` | Dev server (Windows PowerShell) |
| `docker compose up --build` | Docker local run (needs `.env` file) |
| `git push origin main` | Trigger auto-deploy in Coolify (if enabled) |

---

## 🏗️ Project Architecture

**Stack:** FastAPI + Pydantic v2 + Groq/OpenRouter + Docker + Coolify + RapidAPI

**Key Pattern: Middleware → Router → Service → Model**
- **[app/middleware/rapidapi.py](app/middleware/rapidapi.py)** — Custom auth: validates `X-RapidAPI-Proxy-Secret` header; public paths (`/health`, `/docs`, `/openapi.json`) allowed without auth
- **[app/routers/](app/routers/)** — Clean endpoint separation: health check vs. commercial endpoints
- **[app/services/groq_service.py](app/services/groq_service.py)** — AI provider abstraction: tries Groq first, falls back to OpenRouter if configured; includes fallback JSON extraction (markdown wrapping resilience)
- **[app/models.py](app/models.py)** — Pydantic `Literal` types enforce multi-language (en/ar/es/hi/fr), multi-platform (shopify/woocommerce/salla/etc.), and multi-tone (professional/persuasive/luxury/simple) enums

**Fail-Closed Security:** Production mode rejects all commercial traffic without valid `RAPIDAPI_PROXY_SECRET`. See [app/config.py](app/config.py) and [app/main.py lifespan block](app/main.py#L24-L37).

---

## 🔄 GitHub Workflow: Commit → Deploy → RapidAPI

### Deployment Flow

1. **Push to GitHub** (`git push origin main`)
   - Code lands on `origin/main` (public repo assumed)
   - See [COOLIFY_DEPLOY_AR.md Step 1](COOLIFY_DEPLOY_AR.md#الخطوة-1-ارفع-الكود-إلى-github) for first-time setup

2. **Coolify Auto-Deploy** (if enabled in Coolify dashboard)
   - Coolify watches `main` branch
   - On push → Builds `Dockerfile` → Spins up new container on port 8000
   - Environment variables (GROQ_API_KEY, RAPIDAPI_PROXY_SECRET, etc.) injected from Coolify UI
   - Old container stops, new one starts

3. **RapidAPI Integration** (already configured for production)
   - RapidAPI gateway → routes requests to your Coolify domain
   - Gateway adds `X-RapidAPI-Proxy-Secret` header
   - Middleware validates header; passes request to endpoint if valid
   - See [RAPIDAPI_SELLING_GUIDE_AR.md](RAPIDAPI_SELLING_GUIDE_AR.md) for full setup

### When Pushing Code: Pre-Commit Checklist

Before `git push`, ensure:
- [ ] `pytest tests/ -v` passes locally (no real Groq key needed; uses mocked Groq)
- [ ] `docker compose up --build` runs without errors (validates Dockerfile)
- [ ] No `.env` file or secrets in commit (`.gitignore` should block it)
- [ ] No breaking changes to `POST /v1/product-description/generate` request/response schema (RapidAPI clients depend on it)

---

## 🧪 Testing & Local Development

### Test Fixtures

Tests in [tests/test_api.py](tests/test_api.py) use three client fixtures defined in [tests/conftest.py](tests/conftest.py):

- **`client`** — Dev/test mode (`APP_ENV=test`), no auth required
- **`client_with_secret`** — Production mode (`APP_ENV=production`) with valid secret
- **`client_production_no_secret`** — Production mode without secret (validates Fail-Closed behavior)

### Key Test Patterns

- **Groq stub injection** ([conftest.py lines 10–26](tests/conftest.py#L10-L26)): Mocked Groq response injected into `sys.modules` *before* app imports, so no real API calls during test discovery
- **Language/platform/tone validation** ([test_api.py lines 70–115](tests/test_api.py#L70-L115)): All 5 languages tested, including Arabic dialects (formal, saudi_white, gulf_commercial)
- **Provider fallback** ([test_api.py lines 168–211](tests/test_api.py#L168-L211)): Monkeypatch-based test simulates Groq failure → OpenRouter fallback
- **Auth header** ([test_api.py lines 38–53](tests/test_api.py#L38-L53)): Wrong secret → 403, correct secret → 200, production without secret → 403

### Running Tests Locally

```bash
# Activate venv (Windows)
.venv\Scripts\Activate.ps1

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_api.py::test_health_no_secret -v

# Run with coverage (if installed: pip install pytest-cov)
pytest tests/ --cov=app
```

---

## 🔐 Environment Variables

| Var | Required | Where Set | Notes |
|-----|----------|-----------|-------|
| `GROQ_API_KEY` | ✅ | Coolify env vars | Primary AI provider |
| `APP_ENV` | ❌ | Coolify; default: `development` | Controls `is_production` behavior |
| `OPENROUTER_API_KEY` | ❌ | Coolify env vars | Optional fallback; enable with `OPENROUTER_MODEL` |
| `RAPIDAPI_PROXY_SECRET` | ✅ Production only | Coolify env vars | RapidAPI proxy header validation; get from RapidAPI dashboard |
| `LOG_LEVEL` | ❌ | Coolify; default: `INFO` | DEBUG/INFO/WARNING/ERROR |
| `ROOT_PATH` | ❌ | Coolify if using sub-path | For reverse proxy sub-path deployments |

**⚠️ Security:** Never commit `.env` file. Coolify injects environment variables at runtime.

---

## 🚀 Common Workflows for AI Agents

### Adding a New Feature (e.g., new language support)

1. **Update models** → [app/models.py](app/models.py): Add language code to `language: Literal[...]`
2. **Update service** → [app/services/groq_service.py](app/services/groq_service.py): Add prompt template for new language (lines 10–33)
3. **Add test** → [tests/test_api.py](tests/test_api.py): Add language test case (pattern: lines 89–95)
4. **Update docs** → [README.md](README.md) Supported Languages table
5. **Test locally** → `pytest tests/ -v` ✅
6. **Push & deploy** → `git push origin main` → Coolify auto-redeploy → validate `/health` endpoint

### Fixing a Bug in Production

1. **Reproduce locally** → Use `APP_ENV=production` in `.env` + valid `RAPIDAPI_PROXY_SECRET`
2. **Write test** → Add failing test to [tests/test_api.py](tests/test_api.py) that captures the bug
3. **Fix code** → Modify relevant file (usually [app/services/groq_service.py](app/services/groq_service.py) or [app/middleware/rapidapi.py](app/middleware/rapidapi.py))
4. **Test** → `pytest tests/ -v` ✅
5. **Push** → `git push origin main` → Coolify redeploys automatically

### Updating RapidAPI Pricing Plans

1. No code changes needed — pricing is configured in RapidAPI dashboard
2. See [COOLIFY_DEPLOY_AR.md Step 14](COOLIFY_DEPLOY_AR.md#الخطوة-14-اضبط-خطط-التسعير-على-rapidapi) for pricing plan setup

### Monitoring Deployment

- **Healthcheck endpoint** → `curl https://api.yourdomain.com/health` (no auth required)
- **OpenAPI schema** → `https://api.yourdomain.com/openapi.json` (auto-generated by FastAPI)
- **Swagger UI** → `https://api.yourdomain.com/docs` (auto-generated; public in dev, secret required in production)
- **Logs** → Check Coolify dashboard → Select resource → View logs

---

## 📚 Linked Documentation

- **Full Deployment Guide** — [COOLIFY_DEPLOY_AR.md](COOLIFY_DEPLOY_AR.md) (Arabic; comprehensive steps for GitHub → Coolify → RapidAPI)
- **RapidAPI Setup & Pricing** — [RAPIDAPI_SELLING_GUIDE_AR.md](RAPIDAPI_SELLING_GUIDE_AR.md) (Arabic; includes API testing & payment plans)
- **Architecture & File Reference** — [PROJECT_GUIDE_AR.md](PROJECT_GUIDE_AR.md) (Arabic; detailed file-by-file breakdown)
- **API Features & Endpoints** — [README.md](README.md) (English; quick reference for request/response schema)

---

## 🛡️ Security Checklist for PRs & Commits

- [ ] No `GROQ_API_KEY`, `OPENROUTER_API_KEY`, or `RAPIDAPI_PROXY_SECRET` values in code or commit messages
- [ ] `.env` file in `.gitignore` (not committed)
- [ ] Middleware validation ([app/middleware/rapidapi.py](app/middleware/rapidapi.py)) updated if changing auth logic
- [ ] Fail-Closed behavior preserved: production mode without secret → 403 (never 200)
- [ ] No sensitive data in error messages (service layer masks API errors with generic RuntimeError)
- [ ] Tests mock all external API calls (no real Groq/OpenRouter keys needed to run tests)

---

## 🤝 Pattern Summary for Agents

| Task | Key File(s) | Pattern |
|------|------------|---------|
| Add new platform | [models.py](app/models.py#L6-L12) | Add `Literal` enum value |
| Add new language | [groq_service.py](app/services/groq_service.py#L10-L33), [models.py](app/models.py#L8) | New prompt template + Literal enum |
| Change AI logic | [groq_service.py](app/services/groq_service.py) | Service layer abstraction; update fallback strategy if needed |
| Change auth | [middleware/rapidapi.py](app/middleware/rapidapi.py), [config.py](app/config.py) | Update header validation or config logic; preserve Fail-Closed behavior |
| Add/modify endpoint | [routers/product_description.py](app/routers/product_description.py) | Use Pydantic models; log request context; map errors to HTTP status codes |
| Update tests | [tests/test_api.py](tests/test_api.py) | Use three fixtures (client, client_with_secret, client_production_no_secret) |

---

## ⚡ Quick Troubleshooting for Agents

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| Coolify build fails after `git push` | Dockerfile issue or missing env var | Check Coolify → Resource → Logs; verify env vars set in Coolify UI |
| `/health` returns 503 | `GROQ_API_KEY` invalid or Groq API down | Check `.env` file locally; validate key at https://console.groq.com |
| Tests fail with "ModuleNotFoundError: No module named 'groq'" | [conftest.py](tests/conftest.py) mocking failed | Ensure `.venv\Scripts\Activate.ps1` run first; then `pip install -r requirements.txt` |
| RapidAPI returns 403 | Missing or mismatched `X-RapidAPI-Proxy-Secret` | Verify secret in Coolify matches RapidAPI dashboard; check [middleware validation](app/middleware/rapidapi.py#L44-L57) |
| OpenAPI schema (Swagger UI) wrong | `ROOT_PATH` not set | If behind reverse proxy, set `ROOT_PATH` in Coolify env vars |

