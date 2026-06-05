# دليل نشر المشروع على Coolify — خطوة بخطوة للمبتدئين

هذا الدليل يشرح لك كيف تنشر مشروع **Rooz Product Description AI** على سيرفر Coolify من الصفر،
ثم تربطه بـ RapidAPI لبيعه. اتبع الخطوات بالترتيب ولا تتجاوز أي خطوة.

---

## ما الذي ستحتاجه قبل البدء

قبل أن تبدأ، تأكد أنك جهّزت هذه الأشياء:

1. **سيرفر VPS** مثبَّت عليه Coolify (إن لم يكن مثبتاً، انظر القسم الأخير "تثبيت Coolify على VPS").
2. **مفتاح Groq API** — احصل عليه من https://console.groq.com (مجاني). انسخه واحتفظ به.
3. **حساب على GitHub** ورفعت عليه كود المشروع في مستودع (repository).
4. **نطاق (domain)** أو ساب-دومين مثل `api.yourdomain.com` موجّه إلى عنوان IP الخاص بسيرفرك.

> ملاحظة: إن لم يكن لديك دومين الآن، يمكن لـ Coolify توليد رابط مؤقت تلقائياً، لكن للبيع على RapidAPI يُفضّل دومين ثابت.

---

## الخطوة 1 — ارفع الكود إلى GitHub

إن لم تكن رفعت المشروع بعد:

```bash
# داخل مجلد المشروع
git init
git add .
git commit -m "Initial commit - Rooz Product Description AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rooz-product-description-ai.git
git push -u origin main
```

تأكد أن ملف `.env` **غير مرفوع** (يجب أن يبقى سرياً). ملف `.dockerignore` يحميه تلقائياً
من الدخول إلى صورة Docker، لكن أضِف أيضاً ملف `.gitignore` يحوي سطر `.env` لمنع رفعه لـ GitHub.

---

## الخطوة 2 — افتح لوحة تحكم Coolify

1. افتح المتصفح واذهب إلى عنوان Coolify الخاص بك (مثلاً `https://coolify.yourdomain.com` أو `http://YOUR_SERVER_IP:8000`).
2. سجّل الدخول بحسابك.

---

## الخطوة 3 — اربط حساب GitHub بـ Coolify

1. من القائمة الجانبية اضغط **Sources** (أو **Keys & Tokens** حسب الإصدار).
2. اضغط **+ Add** ثم اختر **GitHub App**.
3. اتبع التعليمات لربط حسابك على GitHub، وامنح Coolify صلاحية الوصول إلى المستودع الذي رفعت عليه المشروع.

> إن كان المستودع عاماً (public)، يمكنك تخطّي هذه الخطوة واستخدام رابط Git مباشر في الخطوة التالية.

---

## الخطوة 4 — أنشئ مشروعاً جديداً (Project)

1. من القائمة الجانبية اضغط **Projects**.
2. اضغط **+ Add** وأعطِ المشروع اسماً، مثلاً: `rooz-api`.
3. ادخل إلى المشروع، ثم اختر بيئة **Production**.

---

## الخطوة 5 — أنشئ المورد (Resource) من المستودع

1. اضغط **+ New Resource**.
2. اختر **Public Repository** (إن كان المستودع عاماً) أو **Private Repository (with GitHub App)** إن كان خاصاً.
3. الصق رابط المستودع، مثلاً:
   ```
   https://github.com/YOUR_USERNAME/rooz-product-description-ai
   ```
4. اختر الفرع (Branch): `main`.
5. اضغط **Continue** أو **Load Repository**.

---

## الخطوة 6 — اضبط نوع البناء (Build Pack)

هذه الخطوة مهمة جداً:

1. في إعدادات المورد، ابحث عن خيار **Build Pack**.
2. اختر **Dockerfile** (وليس Nixpacks ولا Docker Compose).
   - السبب: مشروعنا فيه ملف `Dockerfile` جاهز يبني كل شيء بشكل صحيح.
3. تأكد أن **Dockerfile Location** هو `/Dockerfile` (في جذر المشروع).

---

## الخطوة 7 — اضبط المنفذ (Port)

1. ابحث عن حقل **Ports Exposes** أو **Port**.
2. اكتب القيمة:
   ```
   8000
   ```
   - السبب: التطبيق يعمل داخلياً على المنفذ 8000، وهذا ما تخبر به Coolify ليوجّه الحركة إليه.

---

## الخطوة 8 — اضبط الدومين (Domain)

1. ابحث عن حقل **Domains** أو **FQDN**.
2. اكتب الدومين الذي جهّزته، مع `https`، مثلاً:
   ```
   https://api.yourdomain.com
   ```
3. Coolify سيتولّى توليد شهادة SSL (HTTPS) تلقائياً عبر Let's Encrypt.

> تأكد أن سجل DNS من نوع A للدومين يشير إلى IP سيرفرك قبل هذه الخطوة، وإلا ستفشل شهادة SSL.

---

## الخطوة 9 — أضف متغيرات البيئة (Environment Variables) — الأهم

هذه أهم خطوة. كل المفاتيح السرية تُوضع هنا، وليس في الكود.

1. ابحث عن تبويب **Environment Variables** داخل إعدادات المورد.
2. أضِف المتغيرات التالية واحداً واحداً (اضغط **+ Add** لكل واحد):

| المفتاح (Key) | القيمة (Value) | ملاحظات |
|---|---|---|
| `APP_ENV` | `production` | يفعّل وضع الحماية Fail-Closed |
| `LOG_LEVEL` | `INFO` | مستوى السجلات |
| `GROQ_API_KEY` | `gsk_...` | مفتاحك من console.groq.com |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | الموديل المستخدم |
| `RAPIDAPI_PROXY_SECRET` | (اتركه فارغاً مؤقتاً) | ستملؤه في الخطوة 13 |

> **مهم جداً:**
> - في وضع `production`، إذا كان `RAPIDAPI_PROXY_SECRET` فارغاً، فإن كل الـ endpoints التجارية ستُرفض تلقائياً (هذا حماية مقصودة اسمها Fail-Closed).
> - لذلك للاختبار الأولي قبل ربط RapidAPI، يمكنك مؤقتاً وضع `APP_ENV=development` لتجربة الـ endpoint مباشرة. **لا تنسَ إعادته إلى `production` قبل البيع.**

3. اضغط **Save**.

---

## الخطوة 10 — انشر (Deploy)

1. اضغط زر **Deploy** الكبير.
2. ستظهر سجلات البناء (Build Logs) — انتظر حتى يكتمل البناء ويظهر **Running** أو **Healthy**.
3. عادة يستغرق البناء أول مرة من 2 إلى 5 دقائق.

---

## الخطوة 11 — تحقق أن السيرفر يعمل

افتح المتصفح واذهب إلى:

```
https://api.yourdomain.com/health
```

يجب أن ترى رداً مثل:

```json
{"status":"ok","service":"Rooz Product Description AI","version":"1.0.0"}
```

وافتح أيضاً الصفحة الرئيسية:

```
https://api.yourdomain.com/
```

يجب أن تظهر صفحة الهبوط (Landing Page) السوداء الاحترافية.

---

## الخطوة 12 — اختبر الـ endpoint التجاري مباشرة

اختبره من جهازك عبر الـ Terminal (استخدم نفس قيمة `RAPIDAPI_PROXY_SECRET` التي ستضعها لاحقاً،
أو شغّل مؤقتاً بـ `APP_ENV=development` للاختبار بدون سيكرت):

```bash
curl -X POST https://api.yourdomain.com/v1/product-description/generate \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Proxy-Secret: YOUR_SECRET_HERE" \
  -d '{
    "product_name": "Wireless Gaming Mouse",
    "features": ["RGB lighting", "Rechargeable battery", "Low latency"],
    "language": "en",
    "tone": "persuasive",
    "platform": "shopify"
  }'
```

إذا حصلت على رد JSON فيه `short_description` و `bullet_points`، فالسيرفر يعمل بشكل ممتاز. ✅

---

## الخطوة 13 — اربط المشروع بـ RapidAPI

الآن بعد أن أصبح السيرفر يعمل على دومينك، اربطه بـ RapidAPI للبيع:

1. اذهب إلى https://rapidapi.com/provider واضغط **Add New API**.
2. أعطِ الـ API اسماً: `Rooz Product Description AI`.
3. في إعدادات الـ **Base URL**، ضع دومين Coolify الخاص بك:
   ```
   https://api.yourdomain.com
   ```
4. أضِف الـ Endpoint:
   - Method: `POST`
   - Path: `/v1/product-description/generate`
5. اذهب إلى **Settings** الخاصة بالـ API على RapidAPI، وابحث عن **Proxy Secret**
   (يُسمى أحياناً `X-RapidAPI-Proxy-Secret`). انسخ هذه القيمة.
6. ارجع إلى Coolify → Environment Variables → عدّل `RAPIDAPI_PROXY_SECRET`
   والصق فيه القيمة التي نسختها من RapidAPI.
7. تأكد أن `APP_ENV=production`.
8. اضغط **Redeploy** في Coolify لتطبيق التغيير.

> **لماذا هذا السيكرت؟**
> RapidAPI يقف كوسيط بينك وبين العملاء. عندما يرسل العميل طلباً، يمرّره RapidAPI إلى سيرفرك
> مع الهيدر `X-RapidAPI-Proxy-Secret`. سيرفرك يتحقق من تطابقه قبل الرد. هكذا لا يستطيع أحد
> الوصول إلى سيرفرك مباشرة متجاوزاً RapidAPI (ومتجاوزاً الدفع).

---

## الخطوة 14 — اضبط خطط التسعير على RapidAPI

في لوحة RapidAPI، أضِف خطط الاشتراك:

| الخطة | السعر | الطلبات/الشهر |
|---|---|---|
| Free | $0 | 30 |
| Starter | $9 | 500 |
| Pro | $19 | 2,000 |
| Business | $49 | 7,000 |

---

## الخطوة 15 — جرّب كعميل عبر RapidAPI

من صفحة الـ API على RapidAPI، استخدم زر **Test Endpoint**، أو من جهازك:

```bash
curl -X POST https://rooz-product-description-ai.p.rapidapi.com/v1/product-description/generate \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "X-RapidAPI-Host: rooz-product-description-ai.p.rapidapi.com" \
  -d '{"product_name":"Wireless Gaming Mouse","language":"en","tone":"persuasive","platform":"shopify"}'
```

العميل يستخدم `X-RapidAPI-Key` و `X-RapidAPI-Host` **فقط** — ولا يعرف أبداً قيمة `X-RapidAPI-Proxy-Secret`.

---

## التحديثات المستقبلية

عندما تعدّل الكود وترفعه على GitHub:

1. ادفع التغييرات: `git push`.
2. في Coolify اضغط **Redeploy** (أو فعّل **Auto Deploy** ليحدث تلقائياً عند كل push).

---

## حل المشاكل الشائعة

| المشكلة | السبب المحتمل | الحل |
|---|---|---|
| كل الطلبات ترجع 403 | `APP_ENV=production` و `RAPIDAPI_PROXY_SECRET` فارغ | املأ السيكرت أو استخدم `development` مؤقتاً |
| الـ endpoint يرجع خطأ 503 | `GROQ_API_KEY` خاطئ أو فارغ | تحقق من مفتاح Groq |
| فشل شهادة SSL | DNS لا يشير لسيرفرك | تأكد من سجل A في الدومين |
| البناء يفشل | Build Pack خاطئ | اختر **Dockerfile** وليس Nixpacks |
| `/health` لا يعمل | المنفذ خاطئ | تأكد أن Port = 8000 |

---

## مُلحق — تثبيت Coolify على VPS (إن لم يكن مثبتاً)

على سيرفر Ubuntu نظيف، شغّل أمر التثبيت الرسمي:

```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

بعد انتهاء التثبيت، افتح المتصفح على:

```
http://YOUR_SERVER_IP:8000
```

وأنشئ حسابك الأول، ثم تابع من الخطوة 2 أعلاه.

> تأكد أن منافذ `80`, `443`, و `8000` مفتوحة في جدار الحماية (UFW):
> ```bash
> sudo ufw allow 80
> sudo ufw allow 443
> sudo ufw allow 8000
> ```

---

تهانينا! 🎉 مشروعك الآن منشور على Coolify وجاهز للبيع على RapidAPI.
