# دليل بيع Rooz Product Description AI على RapidAPI — للمبتدئين

هذا الدليل يأخذك من "السيرفر يعمل على Coolify" إلى "أول عميل يدفع لك" خطوة بخطوة.
افترض أنك أنهيت نشر المشروع على Coolify بالفعل (راجع `COOLIFY_DEPLOY_AR.md`)
وأن السيرفر يردّ على `https://api.yourdomain.com/health`.

---

## أولاً: ما الذي تغيّر في هذه النسخة؟

طبّقتُ 3 إصلاحات حرجة تؤثر مباشرة على تجربة العميل الدافع:

1. **JSON mode** — الآن نطلب من Groq أن يُرجع JSON مضموناً (`response_format`)، بدل الأمل أن يلتزم. هذا يقلّل أخطاء 502 بشكل كبير.
2. **Timeout 30 ثانية** — لو تأخّر Groq، يفشل الطلب بسرعة بدل تجميد سيرفرك إلى الأبد.
3. **تحقق bullet_points** — نضمن أنها قائمة نصية صالحة، ونحدّها بـ 5 نقاط كحدّ أقصى حسب المواصفات.

> ملاحظات لم تُطبَّق (اختيارية، يمكنك طلبها لاحقاً): إخفاء `/docs` عن العموم، وتنظيف/تحديد طول المدخلات المجمّعة لتقليل تكلفة Groq.

---

## ثانياً: قبل أن تبيع — اختبارات يجب أن تنجح

شغّل هذه على جهازك (وليس داخل الحاوية):

```bash
# 1. الاختبارات
pytest tests/ -v
# يجب أن تمر كل الاختبارات

# 2. بناء Docker
docker build -t rooz-test .
# يجب أن ينجح البناء

# 3. تجربة مباشرة بمفتاح Groq حقيقي (محلياً)
cp .env.example .env
# ضع GROQ_API_KEY حقيقي و APP_ENV=development
docker compose up --build
# ثم جرّب curl على localhost:8000
```

إن نجحت الثلاثة، أنت جاهز للبيع.

---

## ثالثاً: نشر المشروع على RapidAPI خطوة بخطوة

### الخطوة 1 — أنشئ حساب Provider

1. اذهب إلى https://rapidapi.com وسجّل حساباً (مجاني).
2. من القائمة العلوية، اضغط **My APIs** أو اذهب إلى https://rapidapi.com/provider
3. اضغط **Add New API**.

### الخطوة 2 — املأ معلومات الـ API الأساسية

| الحقل | القيمة |
|---|---|
| API Name | `Rooz Product Description AI` |
| Category | `Artificial Intelligence / Machine Learning` أو `eCommerce` |
| Description | AI-powered product description generator for e-commerce in 5 languages (English, Arabic, Spanish, Hindi, French). |

اضغط **Add API**.

### الخطوة 3 — اربط سيرفرك (Base URL)

1. اذهب إلى تبويب **Definition** أو **Settings**.
2. في حقل **Base URL** ضع رابط Coolify الخاص بك:
   ```
   https://api.yourdomain.com
   ```
3. هذا هو الرابط الذي سيرسل إليه RapidAPI طلبات العملاء.

> طريقة أسرع: يمكنك رفع ملف OpenAPI مباشرة. مشروعك يولّده تلقائياً على
> `https://api.yourdomain.com/openapi.json` — حمّله وارفعه في خانة **Import from OpenAPI**.
> هذا يملأ كل الـ endpoints والـ schema تلقائياً.

### الخطوة 4 — عرّف الـ Endpoint

إن لم تستورد OpenAPI، أضِف الـ endpoint يدوياً:

- **Method:** `POST`
- **Path:** `/v1/product-description/generate`
- **Body (JSON):** انسخ المثال من README

أضِف وصفاً واضحاً لكل حقل (product_name, language, tone, platform...) — هذا يساعد العملاء على الفهم ويزيد المبيعات.

### الخطوة 5 — اضبط الـ Proxy Secret (الأمان)

هذه أهم خطوة أمنية:

1. في إعدادات الـ API على RapidAPI، ابحث عن **Security** → **Secret** أو
   `X-RapidAPI-Proxy-Secret`.
2. RapidAPI سيعرض لك قيمة سرية (أو يطلب منك توليد واحدة). **انسخها.**
3. اذهب إلى **Coolify → مشروعك → Environment Variables**.
4. عدّل `RAPIDAPI_PROXY_SECRET` والصق القيمة.
5. تأكد أن `APP_ENV=production`.
6. اضغط **Redeploy** في Coolify.

من الآن: أي طلب لا يحمل هذا السيكرت الصحيح يُرفض بـ 403. هذا يمنع أي شخص
من استخدام سيرفرك مباشرة متجاوزاً RapidAPI (ومتجاوزاً الدفع).

---

## رابعاً: شرح الهيدرات الثلاثة (مهم جداً)

| الهيدر | من يستخدمه | هل العميل يراه؟ |
|---|---|---|
| `X-RapidAPI-Proxy-Secret` | RapidAPI → سيرفرك (داخلي) | ❌ **لا. سرّي تماماً.** |
| `X-RapidAPI-Key` | العميل → RapidAPI | ✅ نعم، مفتاحه الشخصي |
| `X-RapidAPI-Host` | العميل → RapidAPI | ✅ نعم |

**التدفّق:**
```
العميل  ──(X-RapidAPI-Key + Host)──>  RapidAPI  ──(X-RapidAPI-Proxy-Secret)──>  سيرفرك
```

⚠️ **لا تكتب أبداً في توثيق RapidAPI العام أن العميل يستخدم `X-RapidAPI-Proxy-Secret`.**
هذا سيكرت داخلي بينك وبين RapidAPI فقط.

---

## خامساً: أمثلة curl

### للعميل (عبر RapidAPI) — هذا ما تضعه في التوثيق العام

```bash
curl -X POST https://rooz-product-description-ai.p.rapidapi.com/v1/product-description/generate \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: العميل_يضع_مفتاحه_هنا" \
  -H "X-RapidAPI-Host: rooz-product-description-ai.p.rapidapi.com" \
  -d '{"product_name":"Wireless Gaming Mouse","language":"en","tone":"persuasive","platform":"shopify"}'
```

### لك (اختبار مباشر للسيرفر) — لا تنشره للعملاء

```bash
curl -X POST https://api.yourdomain.com/v1/product-description/generate \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Proxy-Secret: السيكرت_الداخلي" \
  -d '{"product_name":"Wireless Gaming Mouse","language":"en","tone":"persuasive","platform":"shopify"}'
```

---

## سادساً: اضبط خطط التسعير

في تبويب **Plans** على RapidAPI:

| الخطة | السعر | الطلبات/الشهر | Rate limit مقترح |
|---|---|---|---|
| Basic (Free) | $0 | 30 | 10/دقيقة |
| Starter | $9 | 500 | 30/دقيقة |
| Pro | $19 | 2,000 | 60/دقيقة |
| Business | $49 | 7,000 | 120/دقيقة |

> نصيحة: اجعل الخطة المجانية صغيرة (30 طلب) — كافية للتجربة، لكنها تدفع الجادّين للترقية.

---

## سابعاً: حدّد تكلفتك قبل التسعير (مهم مالياً)

كل طلب يكلّفك استدعاء Groq واحداً. تحقّق من:

1. تسعير Groq الحالي لموديل `llama-3.3-70b-versatile` على https://groq.com/pricing
2. متوسط التوكنز لكل طلب (مشروعنا يحدّ المخرجات بـ 1500 توكن).
3. احسب: هل سعر الخطة يغطّي تكلفة Groq + هامش ربح؟

> مثال للتفكير: لو كلّفك الطلب الواحد سنتاً واحداً، فخطة Pro (2000 طلب = $20 تكلفة) بسعر $19
> **تخسر**. راجع الأرقام الحقيقية من موقع Groq قبل تثبيت الأسعار.

---

## ثامناً: قبل الضغط على "Publish"

قائمة تحقق نهائية:

- [ ] `pytest tests/ -v` ينجح محلياً
- [ ] `docker build` ينجح
- [ ] السيرفر يردّ على `/health` عبر دومينك
- [ ] `APP_ENV=production` في Coolify
- [ ] `RAPIDAPI_PROXY_SECRET` مملوء ومطابق لقيمة RapidAPI
- [ ] `GROQ_API_KEY` صحيح في Coolify
- [ ] جرّبت طلباً حقيقياً عبر زر **Test Endpoint** في RapidAPI ونجح
- [ ] جرّبت اللغات الخمس (en, ar, es, hi, fr)
- [ ] التوثيق العام لا يذكر `X-RapidAPI-Proxy-Secret`
- [ ] حسبت تكلفة Groq مقابل أسعار الخطط
- [ ] وصف الـ API وأمثلته واضحة وجذّابة

عندما تكتمل كل الخانات، اضغط **Submit for Review** / **Make Public**.

---

## تاسعاً: قائمة المشاكل/الملاحظات المتبقية

أمور لا تمنع البيع لكن يُنصح بمعالجتها لاحقاً:

1. **`/docs` و `/openapi.json` عامّان** — يكشفان بنية الـ API لأي زائر. عادي لكثير من الـ APIs، لكن إن أردت إخفاءهما في production، أخبرني.
2. **لا يوجد rate limiting داخلي** — تعتمد حالياً على rate limiting الخاص بـ RapidAPI فقط. كافٍ للبداية.
3. **لا يوجد تنظيف صارم لطول المدخلات المجمّعة** — عميل خبيث قد يرسل features طويلة جداً لرفع تكلفتك. الحدود الحالية (10 عناصر × 120 حرف) تخفّف هذا لكن لا تلغيه.
4. **لا يوجد caching** — طلبات متطابقة تستدعي Groq كل مرة. إضافة cache تقلّل تكلفتك مستقبلاً.

---

## عاشراً: بعد النشر

- راقب **Analytics** في RapidAPI لمعرفة عدد الطلبات والأخطاء.
- راقب سجلات Coolify بحثاً عن أخطاء 502/503 (مشاكل Groq).
- ردّ على أسئلة العملاء في تبويب **Discussions** بسرعة — يبني السمعة.

بالتوفيق في أول عملية بيع! 🚀
