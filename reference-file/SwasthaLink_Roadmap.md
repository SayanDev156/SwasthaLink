# SwasthaLink — Complete 48-Hour Build Roadmap
> **College TechFest Hackathon · Novelty Score: 80/100**  
> *Converting clinical discharge summaries into patient-readable language with bilingual output, comprehension checks, and WhatsApp delivery*

**Built by:** Suvam Paul · [github.com/Suvam-paul145](https://github.com/Suvam-paul145) · **ownworldmade**  
**Stack:** FastAPI · Gemini 2.5 Flash · React + Vite · Twilio · Supabase · AWS  
**Deploy:** Render (backend) · Vercel (frontend)

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Product Vision & MVP Scope](#2-product-vision--mvp-scope)
3. [System Architecture](#3-system-architecture)
4. [Final Tech Stack](#4-final-tech-stack)
5. [Project Folder Structure](#5-project-folder-structure)
6. [Database & Storage Design](#6-database--storage-design)
7. [API Endpoint Contract](#7-api-endpoint-contract)
8. [Gemini Prompt Architecture](#8-gemini-prompt-architecture)
9. [48-Hour Build Timeline](#9-48-hour-build-timeline)
10. [Phase-by-Phase Build Guide](#10-phase-by-phase-build-guide)
11. [Frontend Component Map](#11-frontend-component-map)
12. [Backend Code Reference](#12-backend-code-reference)
13. [WhatsApp Integration Guide](#13-whatsapp-integration-guide)
14. [Post-MVP Features](#14-post-mvp-features)
15. [Deployment Checklist](#15-deployment-checklist)
16. [Risk Register & Mitigations](#16-risk-register--mitigations)
17. [Demo Day Script](#17-demo-day-script)
18. [Cost Breakdown](#18-cost-breakdown)
19. [Pre-Hackathon Checklist](#19-pre-hackathon-checklist)

---

## 1. Problem Statement

Discharge summaries are written **by doctors, for doctors** — dense clinical language, Latin abbreviations, and drug names patients have never heard of.

| Statistic | Impact |
|---|---|
| **40–80%** of patients forget discharge instructions before reaching home | Medication errors begin before they even leave the building |
| **#1 cause** of preventable hospital readmission is medication non-adherence | Preventable deaths, preventable cost |
| **Bengali-speaking patients** in West Bengal receive instructions in English they cannot read | Language gap compounds health literacy gap |

**SwasthaLink solves this** by taking any clinical discharge summary and producing a simplified, bilingual, audio-readable version — with comprehension verification and WhatsApp delivery — while storing **zero PHI**.

---

## 2. Product Vision & MVP Scope

### End-to-End User Flow

```
Step 1 → Upload or paste clinical discharge summary (text / PDF / photo)
Step 2 → Select role: Patient / Caregiver / Elderly
Step 3 → Gemini 2.5 Flash rewrites in plain English + Bengali (structured JSON)
Step 4 → Patient reads or listens (Web Speech API TTS, lang='bn-IN')
Step 5 → 3 AI-generated MCQs — score <2/3 triggers automatic re-explanation
Step 6 → Simplified summary + medication reminders sent to WhatsApp via Twilio
```

### ★ MVP — 5 Features That MUST Work for Demo

These 5 features are the Minimum Viable Product. **If time runs short, protect these and cut everything else.**

| # | Feature | Endpoint / Component | Why It's Non-Negotiable |
|---|---|---|---|
| 1 | Paste discharge summary → Gemini simplified output | `POST /api/process` | Core demo moment — the product's entire value |
| 2 | Bilingual output: plain English + Bengali | `OutputPanel.tsx` | Novelty differentiator — no other team will have this |
| 3 | 3 comprehension MCQs with score display | `POST /api/quiz/submit` + `QuizPanel.tsx` | Judge wow factor — live proof of understanding |
| 4 | Send simplified summary to WhatsApp via Twilio | `POST /api/send-whatsapp` | Live demo on judge's phone — most memorable moment |
| 5 | Read-aloud via Web Speech API (Bengali TTS) | `useSpeech.ts` hook | Accessibility + novelty — judge hears Bengali on stage |

---

## 3. System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite + TS)                  │
│   ┌──────────────┐  ┌─────────────┐  ┌───────────────────────┐  │
│   │ SummaryInput │  │ RoleSelector│  │      QuizPanel        │  │
│   │  textarea /  │  │  Patient /  │  │  3 MCQ + score gauge  │  │
│   │  PDF upload  │  │  Caregiver /│  │  re-explain trigger   │  │
│   │              │  │  Elderly    │  │                       │  │
│   └──────┬───────┘  └──────┬──────┘  └───────────┬───────────┘  │
│          └─────────────────┴──────────────────────┘              │
│                      POST /api/process                           │
│   ┌──────────────┐  ┌─────────────┐  ┌───────────────────────┐  │
│   │  OutputPanel │  │Medication   │  │    WhatsAppSend       │  │
│   │  EN + Bengali│  │Chart        │  │  phone + preview +    │  │
│   │  TTS buttons │  │(Recharts)   │  │  send button          │  │
│   └──────────────┘  └─────────────┘  └───────────────────────┘  │
│                     Hosted on Vercel                             │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTPS REST
┌──────────────────────────▼───────────────────────────────────────┐
│                  BACKEND (FastAPI + Uvicorn)                     │
│                       Hosted on Render                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  POST /api/process                                      │    │
│  │   1. Validate input (min length, sanitize)              │    │
│  │   2. Call Gemini 2.5 Flash with role-aware prompt       │    │
│  │   3. Strip markdown fences, parse JSON                  │    │
│  │   4. Return: simplified_en, simplified_bn, medications, │    │
│  │              follow_up, warning_signs, quiz, whatsapp   │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐  │
│  │  POST /api/send-wa   │  │  POST /api/upload (Phase 7)      │  │
│  │  Twilio SDK          │  │  Gemini Vision OCR               │  │
│  └──────────────────────┘  └──────────────────────────────────┘  │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐  │
│  │  POST /api/quiz/     │  │  GET /api/health                 │  │
│  │  submit              │  │  UptimeRobot ping target         │  │
│  └──────────────────────┘  └──────────────────────────────────┘  │
└──────────┬─────────────────────────┬────────────────────────────┘
           │                         │
    ┌──────▼──────┐           ┌──────▼──────────┐
    │ Gemini 2.5  │           │  Twilio WhatsApp │
    │ Flash (AI)  │           │  Sandbox API     │
    └──────┬──────┘           └─────────────────┘
           │
    ┌──────▼──────────────────────────────────────┐
    │  Supabase (PostgreSQL)                      │
    │  Session metadata only — zero PHI           │
    ├─────────────────────────────────────────────┤
    │  AWS S3 — document uploads, 24hr auto-del   │
    │  AWS DynamoDB — records, 7-day TTL          │
    └─────────────────────────────────────────────┘
```

### Zero PHI Architecture (Answer for Judges)

```
Clinical text in → RAM only → Gemini API → response → RAM → returned to client
                   ↑                                            ↓
              Never written                          Supabase stores ONLY:
              to disk / DB                           session_id, role, timestamp,
                                                     quiz_score (no clinical text)
```

---

## 4. Final Tech Stack

| Layer | Technology | Version | Why |
|---|---|---|---|
| **AI / LLM** | Google Gemini 2.5 Flash | Latest | Free tier, multilingual, structured JSON, Bengali-native |
| **AI Fallback** | Gemini 1.5 Pro | Latest | If 2.5 Flash is rate-limited |
| **Backend** | FastAPI + Uvicorn | Python 3.11+ | Your home turf, async, Pydantic models |
| **Frontend** | React 18 + Vite + TypeScript | Latest | Fast dev, component-based, your stack |
| **Styling** | Tailwind CSS | 3.x | Utility-first, responsive |
| **Charts** | Recharts | 2.x | Medication timeline + comprehension gauge |
| **TTS** | Web Speech API | Browser native | Zero cost, Bengali `lang='bn-IN'` |
| **WhatsApp** | Twilio Sandbox | Latest SDK | 5-min setup, 100 free msgs, hackathon-ready |
| **Database** | Supabase (PostgreSQL) | Hosted | Session metadata, real-time dashboard, free 500MB |
| **File Storage** | AWS S3 (ap-south-1) | — | PDF uploads, 24hr lifecycle auto-delete |
| **Records** | AWS DynamoDB | — | Structured records, 7-day TTL |
| **Backend Host** | Render | Free tier | Easy Python deploy, free tier |
| **Frontend Host** | Vercel | Free tier | One-push, instant HTTPS |
| **Fonts** | DM Serif Display + DM Sans + Noto Sans Bengali | Google Fonts | Clinical Clarity design system |
| **Cold Start Fix** | UptimeRobot | Free | Pings `/api/health` every 14 min |

---

## 5. Project Folder Structure

```
SwasthaLink/
│
├── README.md                        ← Include demo GIF + live URL
├── .gitignore                       ← MUST include .env, venv/, node_modules/
│
├── backend/
│   ├── main.py                      ← FastAPI app, all routes, CORS
│   ├── gemini_service.py            ← All Gemini API calls + prompt engineering
│   ├── twilio_service.py            ← WhatsApp message sending via Twilio SDK
│   ├── supabase_service.py          ← Session logging (metadata only, zero PHI)
│   ├── s3_service.py                ← PDF upload + 24hr delete lifecycle
│   ├── models.py                    ← Pydantic request/response models
│   ├── prompts.py                   ← All Gemini prompt templates (keep separate!)
│   ├── requirements.txt
│   ├── Procfile                     ← For Render: "web: uvicorn main:app --host 0.0.0.0 --port $PORT"
│   ├── .env                         ← NEVER commit — add to .gitignore
│   └── .env.example                 ← Commit this: template without real keys
│
├── frontend/
│   ├── index.html                   ← Google Fonts imports go here
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── .env                         ← VITE_API_URL=https://your-backend.onrender.com
│   └── src/
│       ├── App.tsx                  ← Main app, step state management (1-5)
│       ├── main.tsx
│       ├── types/
│       │   └── api.ts               ← TypeScript interfaces matching Pydantic models
│       ├── hooks/
│       │   └── useSpeech.ts         ← Web Speech API hook (EN + Bengali TTS)
│       ├── services/
│       │   └── api.ts               ← Axios calls to all backend endpoints
│       └── components/
│           ├── SummaryInput.tsx     ← Textarea + role selector + language toggle
│           ├── RoleSelector.tsx     ← Patient / Caregiver / Elderly buttons
│           ├── OutputPanel.tsx      ← Bilingual output cards + TTS buttons
│           ├── MedicationChart.tsx  ← Recharts pill timeline (Morning→Night)
│           ├── QuizPanel.tsx        ← 3 MCQs + score ring + re-explain trigger
│           ├── WhatsAppSend.tsx     ← Phone input + bubble preview + send button
│           ├── LoadingSpinner.tsx   ← Heartbeat SVG animation during Gemini call
│           └── AlertBanner.tsx      ← Warning sign chips (red/amber/green)
│
├── sample_data/
│   ├── demo_summary.txt             ← 12-drug ICU summary — use this on stage
│   ├── simple_discharge.txt         ← Simple outpatient case for testing
│   └── post_surgery.txt             ← Mid-complexity test case
│
└── docs/
    ├── architecture.png
    └── demo.gif                     ← Record with OBS or Loom
```

---

## 6. Database & Storage Design

### Supabase — `sessions` Table (Zero PHI)

```sql
CREATE TABLE sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  role          TEXT CHECK (role IN ('patient', 'caregiver', 'elderly')),
  language      TEXT CHECK (language IN ('en', 'bn', 'both')),
  quiz_score    INTEGER,           -- 0, 1, 2, or 3
  whatsapp_sent BOOLEAN DEFAULT FALSE,
  re_explained  BOOLEAN DEFAULT FALSE,  -- true if score < 2/3
  log_format    TEXT               -- 'text' | 'pdf' | 'image'
);
```

> ⚠️ **What is NOT stored:** discharge_text, simplified_english, simplified_bengali, patient name, phone number, medication list. **Zero PHI.**

### AWS DynamoDB — `discharge_records` Table

```
Table:         discharge_records
Partition Key: session_id  (String)
TTL Attribute: expires_at  (Number — Unix timestamp, auto-deletes after 7 days)

Attributes:
  session_id      String
  created_at      String  (ISO 8601)
  role            String
  comprehension   Number  (quiz score 0–3)
  whatsapp_sent   Boolean
  expires_at      Number  (created_at + 604800 seconds)
```

### AWS S3 — `discharge-uploads` Bucket

```
Bucket:  discharge-uploads-[your-suffix]
Region:  ap-south-1

Lifecycle Rule:
  Name:        auto-delete-24hr
  Prefix:      uploads/
  Expiration:  1 day after object creation

Object path: uploads/{session_id}/{original_filename}
```

---

## 7. API Endpoint Contract

### `POST /api/process`

**Request:**
```json
{
  "discharge_text": "string (min 50 chars)",
  "role": "patient | caregiver | elderly",
  "language": "en | bn | both"
}
```

**Response:**
```json
{
  "simplified_english": "3–5 short paragraphs in plain English...",
  "simplified_bengali": "সহজ বাংলায় ৩-৫ অনুচ্ছেদ...",
  "medications": [
    {
      "name": "Aspirin",
      "dose": "1 tablet (75mg)",
      "timing": ["morning"],
      "reason": "Prevents blood clots in your heart arteries",
      "important": "Never stop without telling your doctor"
    }
  ],
  "follow_up": {
    "date": "In 2 weeks",
    "with": "Cardiology OPD",
    "reason": "Check wound, blood pressure, and adjust medicines"
  },
  "warning_signs": [
    "Chest pain or tightness",
    "Difficulty breathing",
    "Leg swelling"
  ],
  "comprehension_questions": [
    {
      "question": "Why must you NEVER stop taking Aspirin without asking your doctor?",
      "options": ["A) Helps you sleep", "B) Stopping can cause another blockage", "C) Controls blood pressure", "D) Reduces fever"],
      "correct": "B",
      "explanation": "Aspirin prevents clots — stopping it can trigger another heart attack"
    }
  ],
  "whatsapp_message": "*SwasthaLink* 🏥\nYou had a heart attack. Take *Aspirin 75mg* every morning — never stop.\nFollow-up: Cardiology in 2 weeks.\n🚨 Emergency: chest pain, breathlessness, leg swelling."
}
```

---

### `POST /api/send-whatsapp`

```json
// Request
{
  "phone_number": "+919876543210",
  "message": "string from whatsapp_message field above"
}

// Response
{
  "status": "sent",
  "message": "Message delivered successfully"
}
```

---

### `POST /api/quiz/submit`

```json
// Request
{
  "session_id": "uuid-v4",
  "answers": ["B", "C", "D"],
  "correct_answers": ["B", "C", "D"]
}

// Response
{
  "score": 3,
  "out_of": 3,
  "passed": true,
  "needs_re_explain": false,
  "feedback": "Excellent! You understand your discharge instructions."
}
```

---

### `POST /api/upload` *(Phase 7 — Post-MVP)*

```
Input:  multipart/form-data — field: file (.pdf, .jpg, .png)
Output: { "extracted_text": "...", "file_type": "pdf", "session_id": "uuid" }
```

---

### `GET /api/health`

```json
{ "status": "ok", "service": "SwasthaLink" }
```
> This is the UptimeRobot ping target. Keep it fast — no DB calls.

---

## 8. Gemini Prompt Architecture

### Prompt A — Master Simplification Prompt

```python
ROLE_INSTRUCTIONS = {
    "patient":   "Explain to the patient themselves. Use 'you' and 'your'. Focus on what they need to DO today.",
    "caregiver": "Explain to a family member caring for the patient. Include warning signs and when to call emergency.",
    "elderly":   "Explain to an elderly patient. Very simple words only. No medical terms. Short sentences. Repeat the most important points."
}

MASTER_PROMPT = """
You are a medical translator making discharge summaries understandable for patients.

ROLE: {role_instruction}

DISCHARGE SUMMARY:
{discharge_text}

Respond ONLY with a JSON object. No preamble. No markdown. No backticks. Just raw JSON.

{{
  "simplified_english": "3-5 paragraphs in plain English. Open with '3 things you must do today:' as a bullet list.",
  "simplified_bengali": "Same content in everyday Bengali. Avoid formal or literary Bengali. Use words a village grandmother would understand.",
  "medications": [
    {{
      "name": "plain name (e.g. 'heart tablet' not 'Metoprolol')",
      "dose": "e.g. '1 tablet'",
      "timing": ["morning", "evening"],
      "reason": "1 sentence why — plain English",
      "important": "1 critical warning if any, else null"
    }}
  ],
  "follow_up": {{
    "date": "exact date or 'Ask your doctor'",
    "with": "which doctor or department",
    "reason": "why in plain language"
  }},
  "warning_signs": ["3–5 go-to-emergency symptoms in plain language"],
  "comprehension_questions": [
    {{
      "question": "Simple factual question about the single most critical instruction",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct": "A|B|C|D",
      "explanation": "1 sentence why this matters"
    }}
  ],
  "whatsapp_message": "Under 500 chars. WhatsApp *bold* format. Emojis. Condition in 1 line. Top 3 meds. Follow-up. Emergency signs."
}}
"""

# Generation config — critical for medical content
generation_config = {
    "temperature": 0.3,       # Lower = more consistent, deterministic
    "max_output_tokens": 4096
}
```

---

### Prompt B — Re-Explanation Prompt (score < 2/3)

```python
RE_EXPLAIN_PROMPT = """
The patient scored {score}/3 on their comprehension quiz.
They struggled with: {failed_topics}

Rewrite the discharge instructions in EVEN SIMPLER language:
- Use only words a 10-year-old would know
- Replace ALL remaining medical terms with everyday equivalents
- Every instruction = one short sentence
- Add "This means:" before explaining each medical concept

Previous simplified version:
{previous_simplified}

Return ONLY simplified_english and simplified_bengali as JSON. No other fields.
"""
```

---

### Prompt C — OCR Extraction (Phase 7)

```python
OCR_PROMPT = """
This is a photo or scan of a medical discharge document.
Extract ALL text exactly as visible. Preserve structure and line breaks.
If a word is unclear, write [unclear].
Return only the raw extracted text. No commentary.
"""
```

---

## 9. 48-Hour Build Timeline

```
Hour  0 ──────────────────────────────────────────── Hour 48
│                                                          │
│  PHASE 0   Pre-start setup          (45 min)            │
│  PHASE 1   Core backend             (Hours 0–3)         │
│  PHASE 2   Gemini prompt eng.       (Hours 3–7)   ← HARDEST
│  PHASE 3   Frontend base            (Hours 7–11)        │
│  PHASE 4   Quiz + medication chart  (Hours 11–15)       │
│  PHASE 5   WhatsApp full flow       (Hours 15–18)       │
│  PHASE 6   UI polish + roles        (Hours 18–22)       │
│  PHASE 7   Advanced features        (Hours 22–26)       │
│  PHASE 8   Deploy                   (Hours 26–34)       │
│  PHASE 9   Testing + bug fixes      (Hours 34–40)       │
│  PHASE 10  Demo prep                (Hours 40–48)       │
│                                                          │
```

### Summary Table

| Phase | Hours | Deliverable | Difficulty |
|---|---|---|---|
| 0 | Pre-start | All accounts, keys, repo live | 🟢 Easy |
| 1 | 0–3 | `curl /api/process` returns valid JSON | 🟡 Medium |
| 2 | 3–7 | Perfect structured JSON from real ICU summary | 🔴 Hard |
| 3 | 7–11 | End-to-end: paste → bilingual output → TTS | 🟡 Medium |
| 4 | 11–15 | Quiz works, score ring, medication chart renders | 🟡 Medium |
| 5 | 15–18 | Message received on real phone | 🟡 Medium |
| 6 | 18–22 | Roles visually different, mobile responsive | 🟢 Easy |
| 7 | 22–26 | PDF upload + auto re-explain on low score | 🔴 Hard |
| 8 | 26–34 | Live URLs on Render + Vercel, end-to-end tested | 🟡 Medium |
| 9 | 34–40 | 3 different summaries tested, edge cases handled | 🟢 Easy |
| 10 | 40–48 | 5 full rehearsals, backup recording, pitch ready | 🟢 Easy |

---

## 10. Phase-by-Phase Build Guide

### Phase 0 · Pre-Start (45 minutes before clock starts)

Do this before the hackathon begins — none of it is building.

```bash
# Accounts to create if not done
# 1. aistudio.google.com       → Gemini API key
# 2. twilio.com/try-twilio     → Account SID + Auth Token + sandbox number
# 3. supabase.com              → New project → URL + anon key
# 4. AWS Console               → S3 bucket + DynamoDB table + IAM user with keys
# 5. render.com                → Connect GitHub
# 6. vercel.com                → Connect GitHub

# Create repo and clone
git init SwasthaLink && cd SwasthaLink
git remote add origin https://github.com/Suvam-paul145/SwasthaLink

# Create backend env file
touch backend/.env
# Fill: GEMINI_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
#       TWILIO_WHATSAPP_NUMBER, SUPABASE_URL, SUPABASE_KEY,
#       AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME

# Save demo ICU summary
mkdir sample_data
# → paste 12-drug ICU summary into sample_data/demo_summary.txt

# Join Twilio sandbox on your own phone right now
# → WhatsApp "join [your-word]" to +1 415 523 8886
```

**Checkpoint:** All keys in `.env`, `python -c "import fastapi, google.generativeai, twilio"` passes without error.

---

### Phase 1 · Core Backend (Hours 0–3)

```bash
mkdir backend && cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn google-generativeai twilio python-dotenv \
            pydantic httpx supabase boto3 python-multipart
```

**Build in this order:**

1. `models.py` — Pydantic models (30 min)
2. `prompts.py` — Master prompt template (20 min)
3. `gemini_service.py` — API call + JSON parse + error handling (45 min)
4. `twilio_service.py` — Send WhatsApp function (20 min)
5. `main.py` — FastAPI routes + CORS (30 min)
6. `supabase_service.py` — `log_session()` function (20 min)

**Checkpoint:**
```bash
uvicorn main:app --reload
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"discharge_text":"Patient discharged on Metformin 500mg twice daily for Type 2 Diabetes. Follow up with Dr. Sharma in 4 weeks.", "role":"patient", "language":"both"}'
# Must return: valid JSON with simplified_english, simplified_bengali, quiz questions
```

---

### Phase 2 · Gemini Prompt Engineering (Hours 3–7)

This is the most important block. A weak prompt destroys the product.

```
Task 1 (60 min): Build and test master prompt
  → Paste demo_summary.txt → run it
  → Check: Is Bengali actually everyday language (not literary)?
  → Check: Are medication names in plain language?
  → Check: Do MCQ questions make sense?
  → Check: Does JSON parse without errors every time?

Task 2 (60 min): Iterate until reliable
  → If Bengali is too formal: add "Use words a village grandmother would use"
  → If JSON fails: add stricter "NO markdown, NO backticks, ONLY raw JSON" line
  → If medications confusing: add "Rename each medicine to its plain purpose"
  → Test with 3 lengths: short (Metformin only), medium, complex ICU

Task 3 (60 min): Error handling and edge cases
  → Wrap json.loads() in try/except
  → Add re.sub() to strip ```json fences if Gemini adds them
  → Test: empty input → 400 error
  → Test: 5-word input → validation error
  → Test: non-English input → Gemini still handles it
```

**Checkpoint:** Paste 12-drug ICU summary → clean parseable JSON in under 6 seconds. Bengali reads naturally. Run it 5 times — same structure every time.

---

### Phase 3 · Frontend Base (Hours 7–11)

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install axios recharts tailwindcss @tailwindcss/forms
npx tailwindcss init -p
```

**Add to `index.html`:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap" rel="stylesheet">
```

**Build in this order:**

1. `types/api.ts` — TypeScript interfaces (20 min)
2. `services/api.ts` — Axios wrapper functions (20 min)
3. `App.tsx` — Step state machine 1–5 (30 min)
4. `SummaryInput.tsx` — Textarea + role/language selectors (40 min)
5. `LoadingSpinner.tsx` — Heartbeat SVG animation (20 min)
6. `OutputPanel.tsx` — English + Bengali cards + TTS buttons (50 min)
7. `hooks/useSpeech.ts` — Web Speech API hook (30 min)

**Checkpoint:** Paste summary → click Simplify Now → see bilingual output → click Read Aloud → hear Bengali voice from browser.

---

### Phase 4 · Quiz + Medication Chart (Hours 11–15)

```
Task 1 (90 min): QuizPanel.tsx
  → Render 3 MCQs from API response (dynamic, not hardcoded)
  → Click option → disable all options in that question
  → Show green (correct) / red (wrong) + reveal correct if wrong
  → Submit → show score ring (SVG or Recharts RadialBarChart)
  → Score < 2/3 → show "Explain this differently" button
  → That button → POST /api/process again with re_explain=true param
  → Replace OutputPanel content with new simpler version

Task 2 (90 min): MedicationChart.tsx
  → Parse medications[] from API response — do not hardcode
  → 4-column grid: Morning / Afternoon / Evening / Night
  → Each medication = colored pill badge in correct slot
  → Color by type: heart=teal, blood-thinner=red, antibiotic=blue
  → Click badge → tooltip shows reason + important warning
```

**Checkpoint:** QuizPanel renders from real API data for any summary, not just the demo. Score ring animates. Medication chart correctly places pills from a fresh ICU summary.

---

### Phase 5 · WhatsApp Full Flow (Hours 15–18)

```
Task 1 (45 min): WhatsAppSend.tsx
  → Phone number input with +91 default prefix
  → Preview bubble showing exactly what the WhatsApp message will look like
  → "Send to WhatsApp" button → POST /api/send-whatsapp
  → Loading state while sending
  → Success: green badge "Message sent! Check the phone."
  → Failure: red banner with error reason + retry

Task 2 (45 min): Real device testing
  → Send to your own phone
  → Verify formatting: *bold* renders, emojis display on Android + iOS
  → Verify message stays under 500 characters
  → Test with a second phone (judge simulation)

Task 3 (30 min): Message quality check
  → Read the WhatsApp message out loud — does it make sense?
  → Would a patient with no medical knowledge understand it?
  → Trim if too long, add emojis if too plain
```

**Checkpoint:** Send a real message from UI → receive it on your phone → clean formatting → under 500 chars.

---

### Phase 6 · UI Polish + Role Differentiation (Hours 18–22)

**Design tokens (from your proposal):**
```css
--navy:    #0A1628;   /* background */
--teal:    #00D4AA;   /* primary accent */
--font-display: 'DM Serif Display';
--font-body:    'DM Sans';
--font-bengali: 'Noto Sans Bengali';
```

```
Task 1 (60 min): Make role differences visible
  → Patient panel:   "You must..." framing, concise
  → Caregiver panel: adds "Watch for these signs..." section
  → Elderly panel:   larger font (18px body), shorter paragraphs, bold key words, simple Bengali

Task 2 (60 min): Mobile responsiveness
  → OutputPanel: 1 column (stacked) on screens under 640px
  → MedicationChart: 2-column grid on mobile instead of 4
  → All buttons: full width on mobile
  → Test at 375px width in Chrome DevTools

Task 3 (60 min): Loading states + error handling
  → Heartbeat SVG animation during Gemini call (show this — it's a wow moment)
  → Skeleton placeholders for OutputPanel while loading
  → Toast notification for errors (not alert())
  → Input validation: min 50 chars, max 5000 chars, show character count
```

**Checkpoint:** Show app to a non-technical person. They should navigate all 5 steps without any guidance from you.

---

### Phase 7 · Advanced Features (Hours 22–26)

*Build only after Phases 1–6 are stable.*

```
Feature 1 (2h): PDF / Image Upload — Gemini Vision OCR
  → File input accepting .pdf, .jpg, .png
  → FileReader API → base64 → POST /api/upload
  → Backend: Gemini Vision prompt → extract text → return string
  → Feed extracted text directly into /api/process
  → Edge case: unreadable scan → "Could not extract text, please type manually"

Feature 2 (1h): Re-explain on low quiz score
  → Already wired in Phase 4 — just verify it works end-to-end
  → Add "Simplified further" badge on output card after re-explanation
  → Log re_explained=True to Supabase session

Feature 3 (1h): Supabase live session counter
  → Real-time subscription on sessions table: count of rows
  → Small counter in navbar: "X summaries simplified so far"
  → This is a powerful demo moment — shows live usage by other sessions
```

---

### Phase 8 · Deployment (Hours 26–34)

See [Section 15](#15-deployment-checklist) for full step-by-step.

| Sub-task | Time |
|---|---|
| Backend → Render (Procfile, env vars, test live URL) | 2h |
| UptimeRobot setup (prevent cold start) | 15 min |
| Frontend → Vercel (root dir, env var, test live URL) | 1h |
| Update Render CORS with Vercel URL | 15 min |
| Full end-to-end test on live production URLs | 2h |
| Mobile browser test (Chrome on Android) | 30 min |

---

### Phase 9 · Testing + Bug Fixes (Hours 34–40)

| Test Case | Input | Expected Output |
|---|---|---|
| 12-drug ICU summary | `demo_summary.txt` | Full JSON, 12 medications, 3 quiz questions |
| Simple outpatient discharge | "Metformin 500mg twice daily" | 1–2 meds, basic quiz, short Bengali |
| Empty input | `""` | 400 HTTP error with friendly message |
| Too short input | `"Ok discharge"` | Validation error: "minimum 50 characters" |
| Non-English input | Bengali text | Gemini handles it, returns bilingual output |
| WhatsApp unjoined | Random phone number | Friendly error: "recipient must join sandbox" |
| Bengali TTS unavailable | Old browser / no Bengali voice | Graceful fallback to English TTS |
| Gemini malformed JSON | (rare, simulate by breaking prompt) | try/except returns 500 with clear message |

---

### Phase 10 · Demo Prep (Hours 40–48)

```
1. Run the full 5-step demo flow without stopping — 5 times in a row
2. Time it — must be under 3 minutes
3. Record a backup screen recording with OBS or Loom (in case WiFi dies)
4. Ask 2 judges to join Twilio sandbox 1 hour before demo
5. Warm up Render by opening /api/health in a browser 5 min before your slot
6. Have demo_summary.txt open and ready to paste in a separate tab
7. Prepare HIPAA answer (see Section 17)
8. Know your 3 statistics: 40-80%, #1 cause, 1 day deployment
```

---

## 11. Frontend Component Map

```
App.tsx
│  state: step (1–5), apiResponse, sessionId, role, language
│
├─ Step 1: SummaryInput.tsx
│    props: onSubmit(text, role, language)
│    state: text, role, language, isLoading
│    → on submit: calls api.processSummary() → sets apiResponse → goStep(2)
│
├─ Step 2: OutputPanel.tsx
│    props: data (apiResponse), role
│    → useSpeech('en-GB')  — English TTS button
│    → useSpeech('bn-IN')  — Bengali TTS button
│    → AlertBanner.tsx — warning_signs chips
│    → on Next: goStep(3)
│
├─ Step 3: MedicationChart.tsx
│    props: medications[]
│    state: selectedMed (tooltip)
│    → Recharts BarChart with custom pill shapes
│    → on Next: goStep(4)
│
├─ Step 4: QuizPanel.tsx
│    props: questions[], sessionId
│    state: answers[], score, submitted, needsReExplain
│    → on submit: calls api.submitQuiz() → shows score ring
│    → score < 2: shows ReExplainButton
│       → calls api.processSummary() with re_explain=true
│       → replaces OutputPanel content on return to Step 2
│    → on Next: goStep(5)
│
└─ Step 5: WhatsAppSend.tsx
     props: message (from apiResponse.whatsapp_message), sessionId
     state: phoneNumber, sent, error
     → WhatsAppPreview.tsx (bubble preview)
     → on send: calls api.sendWhatsApp() → success / error state
```

### `useSpeech.ts` Hook

```typescript
import { useRef, useState } from 'react';

export function useSpeech(lang: 'en-GB' | 'bn-IN') {
  const [isSpeaking, setIsSpeaking] = useState(false);

  const speak = (text: string) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = lang;
    utt.rate = 0.85;
    utt.onstart = () => setIsSpeaking(true);
    utt.onend = () => setIsSpeaking(false);
    utt.onerror = () => {
      setIsSpeaking(false);
      // Graceful fallback: if Bengali voice unavailable, use English
      if (lang === 'bn-IN') {
        const fallback = new SpeechSynthesisUtterance(text);
        fallback.lang = 'en-GB';
        window.speechSynthesis.speak(fallback);
      }
    };
    window.speechSynthesis.speak(utt);
  };

  const stop = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  return { speak, stop, isSpeaking };
}
```

### `services/api.ts`

```typescript
import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  processSummary: (data: {
    discharge_text: string;
    role: 'patient' | 'caregiver' | 'elderly';
    language: 'en' | 'bn' | 'both';
    re_explain?: boolean;
    previous_simplified?: string;
  }) => axios.post(`${BASE}/api/process`, data).then(r => r.data),

  submitQuiz: (data: {
    session_id: string;
    answers: string[];
    correct_answers: string[];
  }) => axios.post(`${BASE}/api/quiz/submit`, data).then(r => r.data),

  sendWhatsApp: (data: {
    phone_number: string;
    message: string;
  }) => axios.post(`${BASE}/api/send-whatsapp`, data).then(r => r.data),
};
```

---

## 12. Backend Code Reference

### `main.py`

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ProcessRequest, ProcessResponse, WhatsAppRequest, QuizSubmitRequest
from gemini_service import process_discharge_summary
from twilio_service import send_whatsapp_message
from supabase_service import log_session
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="SwasthaLink API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        os.getenv("FRONTEND_URL", "https://SwasthaLink.vercel.app")
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process", response_model=ProcessResponse)
async def process_summary(request: ProcessRequest):
    if len(request.discharge_text.strip()) < 50:
        raise HTTPException(400, "Summary too short — minimum 50 characters")
    result = await process_discharge_summary(
        text=request.discharge_text,
        role=request.role,
        language=request.language,
        re_explain=getattr(request, 're_explain', False),
        previous_simplified=getattr(request, 'previous_simplified', None)
    )
    await log_session(role=request.role, language=request.language)
    return result

@app.post("/api/send-whatsapp")
async def send_whatsapp(req: WhatsAppRequest):
    success = await send_whatsapp_message(req.phone_number, req.message)
    if not success:
        raise HTTPException(500, "WhatsApp delivery failed. Verify Twilio sandbox.")
    return {"status": "sent"}

@app.post("/api/quiz/submit")
async def submit_quiz(req: QuizSubmitRequest):
    score = sum(1 for a, c in zip(req.answers, req.correct_answers) if a == c)
    return {
        "score": score,
        "out_of": len(req.correct_answers),
        "passed": score >= 2,
        "needs_re_explain": score < 2,
        "feedback": {3: "Excellent!", 2: "Good — review a few things.", 1: "Let's try again.", 0: "No worries — we'll explain differently."}[score]
    }

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "SwasthaLink"}
```

---

### `requirements.txt`

```
fastapi==0.111.0
uvicorn[standard]==0.30.0
google-generativeai==0.7.0
twilio==9.0.4
python-dotenv==1.0.0
pydantic==2.7.0
httpx==0.27.0
supabase==2.3.0
boto3==1.34.0
python-multipart==0.0.9
```

---

### `Procfile` (for Render)

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

### `.env.example` (Commit this, never `.env`)

```bash
GEMINI_API_KEY=your_gemini_api_key_here
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=discharge-uploads-yourname
FRONTEND_URL=https://SwasthaLink.vercel.app
```

---

## 13. WhatsApp Integration Guide

### Twilio Sandbox Setup (5 minutes)

```
1. Go to: console.twilio.com → Messaging → Try WhatsApp
2. Click "Activate Sandbox"
3. Note your sandbox number (e.g. +1 415 523 8886)
4. Note your join code (e.g. "join silver-elephant")
5. Scan QR code with your own phone to join
6. Copy ACCOUNT_SID and AUTH_TOKEN from Twilio dashboard home
7. Store in backend/.env — never commit to GitHub
```

### Demo Day Setup

```
1 hour before your slot:
  → Re-join sandbox to reset the 72hr timer
  → Ask 2 judges to WhatsApp "join silver-elephant" to +1 415 523 8886
  → Verify by sending yourself a test message from the production UI
  → Take a screenshot of WhatsApp message on your phone as backup

On stage (while loading app):
  "Can one of you open WhatsApp right now and text 'join silver-elephant'
   to +1 415 523 8886? It takes 30 seconds and then I'll send the patient
   instructions directly to your phone."
```

### WhatsApp Message Format

```
*SwasthaLink* 🏥

You had a heart attack. A stent was placed to open the blockage.

*💊 Your 3 most important medicines:*
• *Aspirin 75mg* — every morning (NEVER stop)
• *Clopidogrel 75mg* — every morning, 12 months
• *Warfarin 3mg* — every night

*📅 See your doctor:* Cardiology OPD in 2 weeks

*🚨 Go to emergency if:*
chest pain · breathlessness · leg swelling

_Powered by SwasthaLink · ownworldmade_
```

---

## 14. Post-MVP Features

Build these only after all 5 MVP features are stable. Listed in priority order.

| Priority | Feature | When | Hours | Impact |
|---|---|---|---|---|
| 1 | PDF/image upload (Gemini Vision OCR) | Phase 7 | 22–24 | Patient can photograph printed discharge slip |
| 2 | Medication timeline chart (Recharts) | Phase 4 | 11–15 | Visual — patients who can't read still understand |
| 3 | Re-explain on low quiz score | Phase 7 | 24–26 | AI doesn't give up on the patient |
| 4 | Supabase live session counter | Phase 1 | 1–2 | Demo moment: "X summaries simplified so far" |
| 5 | AWS S3 + DynamoDB records | Phase 1 | 1–3 | Enterprise credibility + HIPAA auto-delete story |
| 6 | UptimeRobot cold-start prevention | Phase 8 | 30–33 | **Critical** — prevents 30s cold start killing demo |
| 7 | Mobile-responsive + smooth animations | Phase 6 | 18–22 | Judges test on phones |
| 8 | Medication reminders scheduling | Post-hackathon | — | Twilio time-scheduled messages |
| 9 | Hospital admin dashboard | Post-hackathon | — | B2B deployment, aggregate analytics |

---

## 15. Deployment Checklist

### Backend → Render

```bash
# 1. Verify requirements.txt is up to date
pip freeze > requirements.txt

# 2. Create Procfile in backend/
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 3. Push to GitHub
git add . && git commit -m "deploy: backend ready" && git push

# 4. Render Dashboard
#    New Web Service → Connect GitHub repo
#    Root directory:   backend
#    Runtime:          Python 3
#    Build command:    pip install -r requirements.txt
#    Start command:    uvicorn main:app --host 0.0.0.0 --port $PORT

# 5. Add ALL environment variables from .env.example in Render dashboard

# 6. Test live URL
curl https://your-app.onrender.com/api/health
# Must return: {"status": "ok", "service": "SwasthaLink"}
```

### Frontend → Vercel

```bash
# 1. Test build locally first
cd frontend && npm run build    # must complete with zero errors

# 2. Set production API URL
echo "VITE_API_URL=https://your-app.onrender.com" > .env

# 3. Push to GitHub
git add . && git commit -m "deploy: frontend ready" && git push

# 4. Vercel Dashboard
#    New Project → Import from GitHub
#    Root directory: frontend
#    Framework:      Vite
#    Add env var:    VITE_API_URL = https://your-app.onrender.com
#    Click Deploy

# 5. Update Render CORS
#    → Add FRONTEND_URL = https://your-app.vercel.app in Render env vars
#    → Manually redeploy Render service

# 6. End-to-end test on both live URLs
#    → Upload demo summary → verify bilingual output
#    → Send WhatsApp to your phone → verify delivery
```

### UptimeRobot (Prevent Cold Start)

```
1. uptimerobot.com → Create free account → Add New Monitor
2. Monitor Type: HTTP(s)
3. URL: https://your-app.onrender.com/api/health
4. Monitoring Interval: 14 minutes
5. Enable email alerts
→ This keeps Render alive and prevents the 30-second cold start on demo day
```

---

## 16. Risk Register & Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Gemini returns malformed JSON | Medium | High | `re.sub()` strip markdown + `try/except` + log raw response for debugging |
| Render cold start (30s) during demo | **High** | **Critical** | UptimeRobot pings every 14 min. Warm up manually 5 min before your slot. |
| Twilio sandbox expired (72hr limit) | Low | High | Re-join 1hr before demo. Screenshot WhatsApp message as backup. |
| Bengali TTS unavailable in browser | Medium | Medium | Graceful fallback to English TTS. Show Bengali text visually. Never crash. |
| Judges ask "Is this HIPAA compliant?" | **Certain** | High | *(Prepared answer below in Section 17)* |
| AWS credentials / S3 write fails | Low | Low | S3 is post-MVP. Supabase is primary session log — not affected. |
| WhatsApp message not received on stage | Medium | High | Pre-test 2hrs before. Screenshot backup on your phone. |
| Demo exceeds 3 minutes | Medium | Medium | Practice 5 times. Know exactly which step to skip if running long. |
| Gemini rate limiting (15 RPM free) | Low | Medium | Demo = 1 request per 4 seconds minimum. Well within limits. |
| React build fails on Vercel | Low | High | Test `npm run build` locally before every push to GitHub. |

---

## 17. Demo Day Script

### Setup (15 minutes before your slot)

```
1. Open app fullscreen in Chrome on your laptop
2. Have demo_summary.txt open in a separate tab — ready to copy-paste
3. Ask 1–2 judges: "Can you WhatsApp 'join [your-code]' to +1 415 523 8886?"
4. Keep your own phone as WhatsApp backup
5. Open https://your-app.onrender.com/api/health to warm up Render
6. Open Supabase dashboard — have session counter visible
```

---

### The 3-Minute Demo

**[0:00–0:30] The Hook**

> *"Every year, millions of patients leave hospitals with a document like this."*

*[Paste the 12-drug ICU summary — show the dense jargon on screen]*

> *"Aspirin 75mg OD, Clopidogrel dual antiplatelet, Ramipril 2.5mg titrate in 2-slash-52. They can't understand it. Studies show 40 to 80 percent forget their instructions before they even reach home. Medication non-adherence is the number one cause of hospital readmission. We built SwasthaLink."*

---

**[0:30–1:30] Core Demo**

*[Select Patient role → Both Languages → click Simplify Now]*

*[Heartbeat animation plays for ~6 seconds]*

> *"In about 8 seconds, 12 drugs and complex clinical language become '3 things you must do today' — in plain English and Bengali. Any patient, any language. No app download required."*

*[Click Read Aloud on Bengali panel]*

> *"And they can hear it. In Bengali. Using the browser's own speech engine — zero additional cost, works on any phone with a browser."*

---

**[1:30–2:00] Comprehension Check**

*[Move to quiz panel]*

> *"Here's what makes SwasthaLink different from a translation tool. The patient proves they understood it."*

*[Answer 3 MCQs live]*

> *"If they score below 2 out of 3, the system calls Gemini again with a simpler prompt. It doesn't give up."*

---

**[2:00–2:30] WhatsApp**

*[Enter judge's number → click Send]*

> *"The medication schedule, follow-up date, and emergency warnings go directly to their WhatsApp. The phone they already have. No signup, no app, no QR code."*

*[Pause — watch judge's phone light up]*

> *"There it is."*

---

**[2:30–3:00] Close**

> *"Zero PHI stored. HIPAA-safe architecture. A hospital can deploy this in one day using their existing WhatsApp Business account. Running cost: under $40 per month for 50 patients a day."*

> *"The only question is — why isn't this already in every hospital?"*

---

### Prepared Answers for Judge Questions

| Question | Your Answer |
|---|---|
| *"Is this HIPAA compliant?"* | "Zero-storage architecture. Clinical text is sent to Gemini, processed in RAM, and discarded after the API call. Nothing is written to disk, database, or log files. Supabase stores only session metadata — role, timestamp, quiz score — with no clinical content. DynamoDB records auto-delete after 7 days via TTL." |
| *"What if Bengali TTS isn't available?"* | "Graceful fallback — the system detects availability and falls back to English TTS automatically. Bengali text is always shown visually regardless of TTS support." |
| *"Can this handle other languages?"* | "Gemini 2.5 Flash is natively multilingual. Bengali is our priority for West Bengal but the prompt extends to Tamil, Hindi, Odia — any language Gemini supports — without changing the architecture." |
| *"How is this different from Google Translate?"* | "Google Translate gives a literal translation of medical jargon. 'Dual antiplatelet therapy' in Bengali is still incomprehensible. We rewrite the content into plain language first, then output Bengali. Comprehension, not translation." |
| *"What's the business model?"* | "B2B SaaS — hospitals pay monthly subscription. At $40/month running cost, hospitals serving 50 patients/day can charge a fraction of the readmission cost they're already absorbing. One prevented readmission pays for months of SwasthaLink." |

---

## 18. Cost Breakdown

### Hackathon (0–48 hours) — $0 Total

| Service | Cost | Notes |
|---|---|---|
| Google Gemini 2.5 Flash | **FREE** | $300 Google AI credit for new accounts |
| Twilio WhatsApp Sandbox | **FREE** | 100 messages/month trial |
| Web Speech API | **FREE** | Browser native, no key required |
| Supabase | **FREE** | 500MB + 50,000 MAU |
| AWS S3 + DynamoDB | **FREE** | Within AWS free tier limits |
| Render | **FREE** | Free tier (has cold start — mitigated by UptimeRobot) |
| Vercel | **FREE** | Free tier, no limits for demo |
| UptimeRobot | **FREE** | 50 monitors free |
| **TOTAL** | **₹0 / $0** | |

### Post-Hackathon (Monthly, 50 patients/day)

| Service | Monthly Cost |
|---|---|
| Google Gemini API | ~$5–15/month |
| Twilio WhatsApp Business | ~$15/month + $0.005/message |
| Render Starter (no cold start) | $7/month |
| Supabase | FREE (or $25/mo Pro) |
| AWS S3 + DynamoDB | ~$1–3/month |
| Vercel | FREE |
| **TOTAL** | **~$28–45/month** |

---

## 19. Pre-Hackathon Checklist

Complete everything below **before the clock starts**.

### Accounts & API Keys
- [ ] Get Gemini API key → [aistudio.google.com](https://aistudio.google.com)
- [ ] Create Twilio account → activate WhatsApp sandbox → note join code and number
- [ ] Create Supabase project → copy URL + anon key
- [ ] Set up AWS account → create S3 bucket + DynamoDB table + IAM user
- [ ] Connect GitHub to Render → connect GitHub to Vercel

### Local Environment
- [ ] Python 3.11 installed → `python --version`
- [ ] Node 18+ installed → `node --version`
- [ ] Create GitHub repo `SwasthaLink` → clone locally
- [ ] Create `backend/.env` with all 10 keys filled in
- [ ] Verify Python imports: `python -c "import fastapi, google.generativeai, twilio"`
- [ ] Run `npm create vite@latest frontend -- --template react-ts` → verify build passes

### Demo Data
- [ ] Save 12-drug ICU summary → `sample_data/demo_summary.txt`
- [ ] Save simple outpatient summary → `sample_data/simple_discharge.txt`
- [ ] Memorize the 3 opening statistics (40–80%, #1 cause, 1 day)
- [ ] Join Twilio sandbox on your own phone → verify you can receive messages

### Quick Command Reference

```bash
# Backend — start local
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Frontend — start local
cd frontend && npm run dev

# Test health
curl http://localhost:8000/api/health

# Test full process
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"discharge_text":"Patient discharged on Metformin 500mg BD for Type 2 Diabetes. Follow up with Dr. Sharma in 4 weeks.","role":"patient","language":"both"}'

# Test WhatsApp
curl -X POST http://localhost:8000/api/send-whatsapp \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+91YOUR_NUMBER","message":"Test from SwasthaLink 🏥"}'

# Build frontend for production
cd frontend && npm run build

# Deploy backend (after Render connected to GitHub)
git add . && git commit -m "feat: backend complete" && git push

# Deploy frontend
cd frontend && vercel --prod
```

---

*SwasthaLink · College TechFest Hackathon · Novelty Score 80/100*  
*Built by Suvam Paul · [github.com/Suvam-paul145](https://github.com/Suvam-paul145) · **ownworldmade***  
*FastAPI · Gemini 2.5 Flash · React · Twilio · Supabase · AWS · Render · Vercel*
