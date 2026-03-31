# SwasthaLink Deployment Guide (Vercel + Render)

This guide covers:
1. Where to get values for your `.env` variables (especially `SENTRY_DSN` + SMTP email alert settings)
2. Full step-by-step deployment of **frontend on Vercel** and **backend on Render**

---

## 0) Security first (very important)

Your current `backend/.env` appears to contain real credentials. Treat them as exposed and rotate them immediately:

- Gemini API key
- Twilio SID/token/API keys
- Supabase keys
- AWS access keys
- GitHub token

After rotating, update values in your local `.env` and in hosting dashboards (Render/Vercel).

---

## 1) Where to get these `.env` values

### 1.1 `SENTRY_DSN=your_sentry_dsn_here`

**Where to get it:**
1. Go to [https://sentry.io](https://sentry.io)
2. Create/login to org
3. Create a project (Python for backend and/or React for frontend)
4. Open **Project Settings → Client Keys (DSN)**
5. Copy the DSN value

**Important for this repo:**
- `SENTRY_DSN` exists in `.env` templates, but backend code currently has no Sentry SDK initialization.
- So this value is currently optional unless you add Sentry instrumentation.

---

### 1.2 Email alert channel values (SMTP)

These are used by `backend/rate_alert_service.py` when `RATE_ALERT_EMAIL_ENABLED=true`.

| Variable | Where to get it | Example / Notes |
|---|---|---|
| `RATE_ALERT_EMAIL_ENABLED` | You set this manually | `true` to enable emails, `false` to disable |
| `SMTP_HOST` | Your mail provider SMTP docs | Gmail: `smtp.gmail.com` |
| `SMTP_PORT` | Your mail provider SMTP docs | `587` for STARTTLS (common) |
| `SMTP_USERNAME` | Your SMTP account username | Usually your email address |
| `SMTP_PASSWORD` | Your SMTP/app password | For Gmail use **App Password**, not normal password |
| `SMTP_USE_TLS` | You set this manually | `true` for port `587` |
| `ALERT_FROM_EMAIL` | A sender email allowed by provider | Should match/align with SMTP account |
| `ALERT_TO_EMAIL` | Recipient inbox(es) you choose | Supports comma-separated emails |

#### Gmail setup (recommended quick path)

1. Enable 2-Step Verification on Google account
2. Generate **App Password**: Google Account → Security → App passwords
3. Use:
   - `SMTP_HOST=smtp.gmail.com`
   - `SMTP_PORT=587`
   - `SMTP_USE_TLS=true`
   - `SMTP_USERNAME=your_gmail@gmail.com`
   - `SMTP_PASSWORD=<16-char-app-password>`

---

## 2) Deployment architecture for this repo

- **Frontend (React + Vite)**: deploy on **Vercel** from repo root
- **Backend (FastAPI)**: deploy on **Render** from `backend` directory

From your codebase:
- Frontend API URL comes from `VITE_API_URL`
- Backend CORS includes `FRONTEND_URL`
- Render backend start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 3) Step-by-step: Deploy backend to Render

### Step 3.1 — Push latest code to GitHub

Make sure branch is up to date and pushed.

### Step 3.2 — Create Render Web Service

1. Open [https://render.com](https://render.com)
2. New → **Web Service**
3. Connect your GitHub repo: `Suvam-paul145/SwasthaLink`
4. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3.3 — Add backend environment variables in Render

Set at minimum:

- `GEMINI_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_NUMBER` (sandbox default: `whatsapp:+14155238886`)
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FRONTEND_URL` (temporarily your Vercel preview URL or later production URL)
- `ENVIRONMENT=production`
- `DEBUG=false`

Optional (only if used):

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `S3_BUCKET_NAME`
- `SENTRY_DSN`
- `RATE_ALERT_*`
- SMTP variables for email alerts
- GitHub alert variables

### Step 3.4 — Deploy and verify backend

After deploy completes, check:

- `https://<your-render-service>.onrender.com/api/health`
- `https://<your-render-service>.onrender.com/docs`

If health is degraded/down, fix missing env vars first.

---

## 4) Step-by-step: Deploy frontend to Vercel

### Step 4.1 — Create Vercel project

1. Open [https://vercel.com](https://vercel.com)
2. New Project → Import `Suvam-paul145/SwasthaLink`
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `.`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 4.2 — Add frontend env var in Vercel

Set:

- `VITE_API_URL=https://<your-render-service>.onrender.com`

Redeploy if you add/change env vars after first deployment.

### Step 4.3 — Verify frontend

Open your Vercel URL and ensure:

- Pages load
- API calls succeed (no CORS error)
- End-to-end flow works

---

## 5) Final CORS sync (critical)

After Vercel URL is ready:

1. Go back to Render service env vars
2. Set `FRONTEND_URL=https://<your-vercel-app>.vercel.app` (or your custom domain)
3. Redeploy backend

This is required because backend CORS allow-list includes `FRONTEND_URL`.

---

## 6) Recommended post-deploy checklist

- [ ] Backend `/api/health` is `ok` or expected `degraded`
- [ ] Frontend can call backend without CORS issues
- [ ] Twilio WhatsApp sandbox joined and test message delivered
- [ ] Supabase logging works
- [ ] (Optional) S3 upload works
- [ ] (Optional) Email alerts test passes after forcing high usage threshold

---

## 7) Optional: keep Render free tier warm

If your Render plan sleeps on inactivity, use an uptime monitor to ping:

- `https://<your-render-service>.onrender.com/api/health`

at regular intervals.

---

## 8) Quick copy template for email alert vars

```dotenv
RATE_ALERT_EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_USE_TLS=true
ALERT_FROM_EMAIL=your_email@gmail.com
ALERT_TO_EMAIL=your_email@gmail.com,another_email@gmail.com
```

---

## 9) Notes about Sentry in this project

- `SENTRY_DSN` is present in env templates.
- Current backend code does not initialize Sentry SDK yet.
- If you want, add Sentry instrumentation first, then set DSN on Render/Vercel.
