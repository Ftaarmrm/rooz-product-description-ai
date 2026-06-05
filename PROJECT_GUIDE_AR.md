# دليل مشروع Rooz Product Description AI — المرجع الشامل

نسخة المشروع: 1.0.0 | آخر تحديث: 2026

---

## ما هو المشروع؟

API بالذكاء الاصطناعي يولّد أوصاف منتجات احترافية للمتاجر الإلكترونية.
مبني بـ FastAPI + Groq، وجاهز للبيع على RapidAPI.

---

## شجرة الملفات الكاملة

```
rooz-product-description-ai/
├── app/
│   ├── __init__.py
│   ├── main.py                      ← نقطة دخول FastAPI
│   ├── config.py                    ← متغيرات البيئة (Settings)
│   ├── models.py                    ← نماذج Pydantic v2
│   ├── middleware/
│   │   └── rapidapi.py              ← حماية X-RapidAPI-Proxy-Secret
│   ├── routers/
│   │   ├── health.py                ← GET /health
│   │   └── product_description.py  ← POST /v1/product-description/generate
│   └── services/
│       └── groq_service.py          ← Groq (أساسي) + OpenRouter (احتياطي)
├── static/
│   └── index.html                   ← Landing page داكنة احترافية
├── tests/
│   ├── conftest.py                  ← fixtures + Groq stub
│   └── test_api.py                  ← 20+ اختبار
├── Dockerfile                       ← Python 3.12-slim, non-root, HEALTHCHECK
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example                     ← انسخه وسمّه .env
├── .gitignore
├── .dockerignore
├── LICENSE                          ← Proprietary
├── README.md                        ← توثيق إنجليزي كامل
├── COOLIFY_DEPLOY_AR.md             ← دليل نشر Coolify بالعربي
├── RAPIDAPI_SELLING_GUIDE_AR.md     ← دليل البيع على RapidAPI بالعربي
└── PROJECT_GUIDE_AR.md              ← هذا الملف
```

---

## متغيرات البيئة — الجدول الكامل

| المتغير | مطلوب | الافتراضي | الوصف |
|---------|--------|-----------|-------|
| `APP_ENV` | ❌ | `development` | `production` أو `development` أو `test` |
| `LOG_LEVEL` | ❌ | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `GROQ_API_KEY` | ✅ | — | مفتاح Groq من console.groq.com |
| `GROQ_MODEL` | ❌ | `llama-3.3-70b-versatile` | موديل Groq |
| `OPENROUTER_API_KEY` | ❌ | — | مفتاح OpenRouter (اتركه فارغاً لتعطيل الاحتياطي) |
| `OPENROUTER_MODEL` | ❌ | `meta-llama/llama-3.3-70b-instruct` | موديل OpenRouter |
| `RAPIDAPI_PROXY_SECRET` | ✅ في production | — | سر RapidAPI (داخلي فقط، لا تعطيه للعملاء) |
| `ROOT_PATH` | ❌ | — | فارغ لـ Coolify العادي |
| `FORWARDED_ALLOW_IPS` | ❌ | `*` | الـ IPs الموثوقة خلف Traefik |

---

## المزوّدون: Groq + OpenRouter

### كيف يعمل النظام

```
طلب العميل
    ↓
Groq (الأساسي)
    ├── نجح → رد فوري
    └── فشل → هل OPENROUTER_API_KEY مضبوط؟
                 ├── لا  → خطأ 503 للعميل
                 └── نعم → OpenRouter (الاحتياطي)
                              ├── نجح → رد للعميل
                              └── فشل → خطأ 503 للعميل
```

### تغيير المزوّدين من Coolify (بدون لمس الكود)

**تغيير موديل Groq:**
```
GROQ_MODEL=llama-3.1-8b-instant
```

**تفعيل OpenRouter كاحتياطي:**
```
OPENROUTER_API_KEY=sk-or-xxxxxxxxxx
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct
```

**تعطيل OpenRouter:**
```
OPENROUTER_API_KEY=
```

**تغيير موديل OpenRouter:**
```
OPENROUTER_MODEL=google/gemma-3-27b-it
```

موديلات OpenRouter المتاحة: https://openrouter.ai/models

**الخطوات دائماً:**
Coolify → مشروعك → Environment Variables → عدّل → Redeploy ✓

---

## الـ Endpoints

### GET /health — عام، بدون حماية
```json
{
  "status": "ok",
  "service": "Rooz Product Description AI",
  "version": "1.0.0"
}
```

### POST /v1/product-description/generate — محمي

**الطلب:**
```json
{
  "product_name": "Wireless Gaming Mouse",
  "features": ["RGB lighting", "Rechargeable battery", "Low latency"],
  "language": "en",
  "tone": "persuasive",
  "platform": "shopify",
  "target_audience": "gamers",
  "arabic_style": "formal"
}
```

**الحقول:**

| الحقل | مطلوب | الافتراضي | القيم |
|-------|--------|-----------|-------|
| `product_name` | ✅ | — | نص 2-150 حرف |
| `features` | ❌ | null | قائمة حتى 10 عناصر، كل عنصر 120 حرف |
| `language` | ❌ | `en` | `en` `ar` `es` `hi` `fr` |
| `tone` | ❌ | `professional` | `professional` `persuasive` `luxury` `simple` |
| `platform` | ❌ | `general` | `general` `shopify` `woocommerce` `salla` `zid` `amazon` `noon` `aliexpress` |
| `target_audience` | ❌ | null | نص حتى 120 حرف |
| `arabic_style` | ❌ | `formal` | `formal` `saudi_white` `gulf_commercial` (فقط مع `language=ar`) |

**الرد:**
```json
{
  "product_name": "Wireless Gaming Mouse",
  "short_description": "...",
  "long_description": "...",
  "bullet_points": ["...", "...", "..."],
  "seo_title": "...",
  "meta_description": "...",
  "language": "en",
  "tone": "persuasive",
  "platform": "shopify"
}
```

---

## اللغات المدعومة

| اللغة | الكود | ملاحظة |
|-------|-------|--------|
| English | `en` | — |
| Arabic | `ar` | يدعم 3 أساليب: formal, saudi_white, gulf_commercial |
| Spanish | `es` | — |
| Hindi | `hi` | بدون Hinglish |
| French | `fr` | — |

---

## أمثلة curl

### للمدير (اختبار مباشر للسيرفر)

```bash
curl -X POST https://api.yourdomain.com/v1/product-description/generate \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Proxy-Secret: YOUR_PROXY_SECRET" \
  -d '{"product_name":"ماوس ألعاب لاسلكي","language":"ar","arabic_style":"gulf_commercial","tone":"persuasive","platform":"salla","features":["إضاءة RGB","بطارية قابلة للشحن","استجابة سريعة"]}'
```

### للعميل (عبر RapidAPI) — ضعه في التوثيق العام

```bash
curl -X POST https://rooz-product-description-ai.p.rapidapi.com/v1/product-description/generate \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: CUSTOMER_API_KEY" \
  -H "X-RapidAPI-Host: rooz-product-description-ai.p.rapidapi.com" \
  -d '{"product_name":"Wireless Gaming Mouse","language":"en","tone":"persuasive","platform":"shopify"}'
```

---

## أمثلة الطلبات للغات الخمس

**English:**
```json
{"product_name":"Smart Watch","language":"en","tone":"luxury","platform":"shopify"}
```

**Arabic (فصحى):**
```json
{"product_name":"ساعة ذكية","language":"ar","arabic_style":"formal","tone":"professional","platform":"salla"}
```

**Arabic (خليجي):**
```json
{"product_name":"ساعة ذكية","language":"ar","arabic_style":"gulf_commercial","tone":"persuasive","platform":"noon"}
```

**Spanish:**
```json
{"product_name":"Reloj Inteligente","language":"es","tone":"persuasive","platform":"general"}
```

**Hindi:**
```json
{"product_name":"स्मार्ट वॉच","language":"hi","tone":"professional","platform":"general"}
```

**French:**
```json
{"product_name":"Montre Connectée","language":"fr","tone":"luxury","platform":"general"}
```

---

## التشغيل المحلي (للاختبار)

```bash
# 1. انسخ ملف البيئة
cp .env.example .env

# 2. عدّل .env وأضف مفتاح Groq
# GROQ_API_KEY=gsk_xxxxxxxxxx
# APP_ENV=development

# 3. ثبّت التبعيات
pip install -r requirements.txt

# 4. شغّل
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

افتح:
- http://localhost:8000 — Landing page
- http://localhost:8000/docs — Swagger UI
- http://localhost:8000/health — Health check

---

## Docker

```bash
# تشغيل
docker compose up --build

# في الخلفية
docker compose up -d --build

# سجلات
docker compose logs -f

# إيقاف
docker compose down
```

---

## الاختبارات

```bash
pytest tests/ -v
```

لا تحتاج مفتاح Groq حقيقي. كل الاستدعاءات مُحاكاة (mocked).

**ما تغطيه الاختبارات:**
- المسارات العامة بدون secret
- حماية 403 في production
- secret صحيح يُرجع 200
- secret خاطئ يُرجع 403
- Validation: product_name فارغ، لغة غير مدعومة، platform خاطئ، tone خاطئ
- اللغات الخمس كلها
- Fallback: Groq يفشل → OpenRouter ينجح
- Fallback: كلاهما يفشل → 503 بدون تسريب تفاصيل

---

## النشر على Coolify (خطوات مختصرة)

1. ارفع المشروع على GitHub
2. Coolify → New Resource → Git Repository
3. Build Pack: **Dockerfile**
4. Port: **8000**
5. Domain: `https://api.yourdomain.com`
6. Environment Variables:
   ```
   APP_ENV=production
   GROQ_API_KEY=gsk_xxxxxxxxxx
   RAPIDAPI_PROXY_SECRET=xxxxxxxxxx
   FORWARDED_ALLOW_IPS=*
   ```
7. Deploy

للتفصيل: راجع `COOLIFY_DEPLOY_AR.md`

---

## الربط مع RapidAPI (خطوات مختصرة)

1. https://rapidapi.com/provider → Add New API
2. Base URL: رابط Coolify
3. أو استورد مباشرة: `https://api.yourdomain.com/openapi.json`
4. Security → Proxy Secret → انسخ القيمة
5. الصقها في `RAPIDAPI_PROXY_SECRET` بـ Coolify → Redeploy
6. Plans → أضف الخطط الأربع

للتفصيل: راجع `RAPIDAPI_SELLING_GUIDE_AR.md`

---

## التسعير المقترح

| الخطة | السعر | الطلبات/شهر |
|-------|-------|-------------|
| Free | $0 | 30 |
| Starter | $9 | 500 |
| Pro | $19 | 2,000 |
| Business | $49 | 7,000 |

---

## الأمان — نقاط لا تتجاهلها

| النقطة | الحالة |
|--------|--------|
| لا مفاتيح في الكود | ✅ |
| Fail-Closed في production | ✅ |
| `X-RapidAPI-Proxy-Secret` سري (لا تنشره) | ✅ |
| أخطاء Groq لا تُرسل للعميل | ✅ |
| `.env` في `.gitignore` و `.dockerignore` | ✅ |
| uvicorn يعمل بمستخدم غير root | ✅ |
| HEALTHCHECK في Dockerfile | ✅ |

---

## الهيدرات الثلاثة — ملخص سريع

```
X-RapidAPI-Proxy-Secret  → RapidAPI ← سيرفرك (سري، داخلي فقط)
X-RapidAPI-Key           → العميل ← RapidAPI (مفتاح العميل الشخصي)
X-RapidAPI-Host          → العميل ← RapidAPI (هوية الـ API)
```

لا تطلب من العميل أبداً `X-RapidAPI-Proxy-Secret`.

---

## License

Proprietary — All Rights Reserved
Copyright (c) 2026 Rooz
