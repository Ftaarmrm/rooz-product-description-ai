# RapidAPI Launch Checklist

## Server

- [ ] Domain works: https://api.rooz-map.store
- [ ] Health works: GET /health
- [ ] OpenAPI works: GET /openapi.json
- [ ] Docs work: GET /docs
- [ ] Favicon does not return 403
- [ ] Main endpoint works with correct X-RapidAPI-Proxy-Secret
- [ ] Main endpoint rejects missing secret with 403
- [ ] Main endpoint rejects wrong secret with 403

## Coolify Environment Variables

- [ ] APP_ENV=production
- [ ] LOG_LEVEL=INFO
- [ ] GROQ_API_KEY is set as Runtime Variable and starts with gsk_
- [ ] GROQ_MODEL=llama-3.3-70b-versatile
- [ ] RAPIDAPI_PROXY_SECRET is set as Runtime Variable
- [ ] FORWARDED_ALLOW_IPS=*
- [ ] ROOT_PATH is empty
- [ ] No real secrets committed to GitHub

## RapidAPI

- [ ] Base URL is https://api.rooz-map.store
- [ ] OpenAPI imported from https://api.rooz-map.store/openapi.json
- [ ] Proxy Secret copied into Coolify
- [ ] Endpoint tested from RapidAPI dashboard
- [ ] Free plan added
- [ ] Starter plan added
- [ ] Pro plan added
- [ ] Business plan added
- [ ] Public description added
- [ ] Pricing checked against Groq cost
- [ ] RapidAPI marketplace URL added to static/index.html after publishing

## Security

- [ ] No secrets committed to GitHub
- [ ] No real keys in README
- [ ] No keys in static/index.html
- [ ] No keys in .env.example
- [ ] Production endpoint fails closed without proxy secret
- [ ] Customers never see X-RapidAPI-Proxy-Secret
