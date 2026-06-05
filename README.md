# Rooz Product Description AI

> AI-powered Product Description API for e-commerce platforms. Generate product descriptions, bullet points, SEO titles, and meta descriptions in 5 languages via a single REST endpoint.

---

## Features

- **5-language support** — English, Arabic, Spanish, Hindi, French
- **Platform-aware** — Shopify, WooCommerce, Salla, Zid, Amazon, Noon, AliExpress, General
- **4 tones** — Professional, Persuasive, Luxury, Simple
- **Arabic styles** — Formal (فصحى), Saudi White, Gulf Commercial
- **Complete SEO package** — SEO title, meta description, bullet points, short & long descriptions
- **Fail-Closed security** — Production rejects all traffic without a valid RapidAPI proxy secret
- **Provider fallback** — Groq is primary; if it fails and OpenRouter is configured, requests fall back automatically with no downtime
- **Docker-ready** — single `docker compose up` to run
- **Coolify-compatible** — deploy as a container with environment variables

---

## Supported Languages

| Language | Code |
|----------|------|
| English  | `en` |
| Arabic   | `ar` |
| Spanish  | `es` |
| Hindi    | `hi` |
| French   | `fr` |

---

## Main Endpoint

```
POST /v1/product-description/generate
```

### Request Body

```json
{
  "product_name": "Wireless Gaming Mouse",
  "features": [
    "RGB lighting",
    "Rechargeable battery",
    "Low latency"
  ],
  "language": "en",
  "tone": "persuasive",
  "platform": "shopify",
  "target_audience": "gamers",
  "arabic_style": "formal"
}
```

**Field rules:**

| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| `product_name` | ✅ | — | 2–150 chars, not blank |
| `features` | ❌ | `null` | Max 10 items, each max 120 chars |
| `language` | ❌ | `en` | `en`, `ar`, `es`, `hi`, `fr` |
| `tone` | ❌ | `professional` | `professional`, `persuasive`, `luxury`, `simple` |
| `platform` | ❌ | `general` | `general`, `shopify`, `woocommerce`, `salla`, `zid`, `amazon`, `noon`, `aliexpress` |
| `target_audience` | ❌ | `null` | Max 120 chars |
| `arabic_style` | ❌ | `formal` | Only used when `language=ar`. Options: `formal`, `saudi_white`, `gulf_commercial` |

### Response Body

```json
{
  "product_name": "Wireless Gaming Mouse",
  "short_description": "Dominate every match with RGB precision and zero-lag wireless freedom.",
  "long_description": "Engineered for serious gamers who refuse to compromise on performance...",
  "bullet_points": [
    "Vibrant RGB lighting with multiple customizable modes",
    "Long-lasting rechargeable battery — no disposables needed",
    "Ultra-low latency wireless connection for competitive gaming"
  ],
  "seo_title": "Wireless Gaming Mouse with RGB & Rechargeable Battery",
  "meta_description": "Shop the Wireless Gaming Mouse with RGB lighting, rechargeable battery, and ultra-low latency for serious gamers.",
  "language": "en",
  "tone": "persuasive",
  "platform": "shopify"
}
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_ENV` | ❌ | `development` | `production`, `development`, or `test` |
| `LOG_LEVEL` | ❌ | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `GROQ_API_KEY` | ✅ | — | Your Groq API key |
| `GROQ_MODEL` | ❌ | `llama-3.3-70b-versatile` | Groq model to use |
| `OPENROUTER_API_KEY` | ❌ | — | Optional fallback. If set, used automatically when Groq fails. |
| `OPENROUTER_MODEL` | ❌ | `meta-llama/llama-3.3-70b-instruct` | OpenRouter model for fallback |
| `RAPIDAPI_PROXY_SECRET` | ✅ in production | — | Secret from RapidAPI dashboard |

---

## Local Development

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd rooz-product-description-ai

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and fill in GROQ_API_KEY

# 5. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

---

## Docker

```bash
# Build and run
cp .env.example .env
# Edit .env with your values

docker compose up --build

# Run in background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop
docker compose down
```

---

## Deploy on Coolify

1. Push the project to a Git repository (GitHub, GitLab, etc.)
2. In Coolify: **New Resource → Git Repository**
3. Select your repository
4. Set **Build Pack** to `Dockerfile`
5. Set **Port** to `8000`
6. Add environment variables in Coolify's UI:
   - `APP_ENV=production`
   - `GROQ_API_KEY=your_key`
   - `RAPIDAPI_PROXY_SECRET=your_secret`
7. Deploy

---

## RapidAPI Integration

### Step 1 — Publish your API on RapidAPI

1. Go to [rapidapi.com/provider](https://rapidapi.com/provider) and create a new API
2. Set your Coolify URL as the base URL (e.g., `https://your-app.coolify.domain`)
3. Add the endpoint: `POST /v1/product-description/generate`
4. In **Settings → Proxy Secret**, copy the `X-RapidAPI-Proxy-Secret` value
5. Set that value as `RAPIDAPI_PROXY_SECRET` in your Coolify environment variables

### Step 2 — How authentication works

| Header | Who uses it | Description |
|--------|-------------|-------------|
| `X-RapidAPI-Proxy-Secret` | **RapidAPI → Your server** | Internal secret. RapidAPI injects this automatically. **Never share with customers.** |
| `X-RapidAPI-Key` | **Customer → RapidAPI** | The customer's personal API key from RapidAPI. Your server never sees this. |
| `X-RapidAPI-Host` | **Customer → RapidAPI** | The API host identifier. Your server never sees this. |

**Flow:** Customer → (X-RapidAPI-Key + X-RapidAPI-Host) → RapidAPI Gateway → (X-RapidAPI-Proxy-Secret) → Your Server

---

## curl Examples

### Internal server test (direct, using proxy secret)

```bash
curl -X POST https://your-app.coolify.domain/v1/product-description/generate \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Proxy-Secret: YOUR_PROXY_SECRET" \
  -d '{
    "product_name": "Wireless Gaming Mouse",
    "features": ["RGB lighting", "Rechargeable battery", "Low latency"],
    "language": "en",
    "tone": "persuasive",
    "platform": "shopify",
    "target_audience": "gamers"
  }'
```

### RapidAPI customer request (via RapidAPI gateway)

```bash
curl -X POST https://rooz-product-description-ai.p.rapidapi.com/v1/product-description/generate \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "X-RapidAPI-Host: rooz-product-description-ai.p.rapidapi.com" \
  -d '{
    "product_name": "Wireless Gaming Mouse",
    "features": ["RGB lighting", "Rechargeable battery", "Low latency"],
    "language": "en",
    "tone": "persuasive",
    "platform": "shopify"
  }'
```

---

## Language Examples

### English (en)

```json
{
  "product_name": "Wireless Gaming Mouse",
  "language": "en",
  "tone": "persuasive",
  "platform": "shopify",
  "features": ["RGB lighting", "Rechargeable battery", "Low latency"]
}
```

### Arabic (ar) — Formal

```json
{
  "product_name": "ماوس ألعاب لاسلكي",
  "language": "ar",
  "arabic_style": "formal",
  "tone": "professional",
  "platform": "salla",
  "features": ["إضاءة RGB", "بطارية قابلة للشحن", "استجابة سريعة"]
}
```

### Arabic (ar) — Saudi White

```json
{
  "product_name": "ماوس ألعاب لاسلكي",
  "language": "ar",
  "arabic_style": "saudi_white",
  "tone": "persuasive",
  "platform": "noon",
  "features": ["إضاءة RGB", "بطارية قابلة للشحن", "استجابة سريعة"]
}
```

### Spanish (es)

```json
{
  "product_name": "Ratón Inalámbrico Gaming",
  "language": "es",
  "tone": "persuasive",
  "platform": "general",
  "features": ["Iluminación RGB", "Batería recargable", "Baja latencia"]
}
```

### Hindi (hi)

```json
{
  "product_name": "वायरलेस गेमिंग माउस",
  "language": "hi",
  "tone": "professional",
  "platform": "general",
  "features": ["RGB लाइटिंग", "रिचार्जेबल बैटरी", "कम विलंबता"]
}
```

### French (fr)

```json
{
  "product_name": "Souris Gaming Sans Fil",
  "language": "fr",
  "tone": "luxury",
  "platform": "general",
  "features": ["Éclairage RGB", "Batterie rechargeable", "Faible latence"]
}
```

---

## Running Tests

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test
pytest tests/test_api.py::test_health_no_secret -v
```

Tests are fully mocked — no real Groq API key is needed for testing.

---

## Pricing

Available on RapidAPI:

| Plan | Price | Requests/month |
|------|-------|----------------|
| Free | $0 | 30 |
| Starter | $9 | 500 |
| Pro | $19 | 2,000 |
| Business | $49 | 7,000 |

---

## Security Notes

- `RAPIDAPI_PROXY_SECRET` is **never exposed** to end users. It is an internal secret between RapidAPI and your server.
- In `production` mode, if `RAPIDAPI_PROXY_SECRET` is not configured, **all commercial endpoints are rejected** (Fail Closed behavior). No accidental open access.
- In `development` or `test` mode, the secret check is skipped for development convenience.
- No API keys are stored in the source code. All secrets are managed via environment variables.

---

## License

Proprietary — All Rights Reserved  
Copyright (c) 2026 Rooz

Unauthorized use, reproduction, or distribution is strictly prohibited.
