# Fitness Bot — WhatsApp Personal Coach

A WhatsApp bot that tracks your nutrition, workouts, water, sleep, and supplements using Claude AI.

## What it does

- **Chat in Hebrew or English** — send text, voice notes, or photos
- **Food tracking** — photo or text → automatic calorie/macro logging with Claude vision
- **Workout logging** — voice note describing your session → structured workout log
- **Strava sync** — runs automatically logged when you finish an activity
- **Apple Health sync** — weight and sleep synced daily via iOS Shortcut
- **Weekly planning** — set your training plan Monday morning, bot adapts to your calendar
- **Daily summary** — WhatsApp message at 8 PM with the day's totals
- **Web dashboard** — progress charts, photos gallery, trends

---

## Setup (one-time, done by developer)

### 1. Get API keys

You'll need accounts for:
- [Anthropic](https://console.anthropic.com) — Claude API key
- [Twilio](https://console.twilio.com) — WhatsApp sandbox
- [OpenAI](https://platform.openai.com) — Whisper transcription
- [Cloudflare R2](https://cloudflare.com) — photo storage (free tier)
- [Strava](https://developers.strava.com) — create an API app
- [Google Cloud](https://console.cloud.google.com) — enable Calendar API, create OAuth credentials

### 2. Deploy on Railway

1. Fork this repo to your GitHub account
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select your forked repo
4. Click **+ Add Service** → **Database** → **PostgreSQL**
5. Click **+ Add Service** → **Database** → **Redis**
6. In your app's **Variables** tab, add all values from `.env.example`
7. Click **Deploy** — Railway builds and starts (~3 minutes)
8. Copy your public URL: `https://your-app.up.railway.app`

### 3. Connect Twilio WhatsApp

1. Twilio Console → Messaging → Try it → WhatsApp
2. Set **"A message comes in"** webhook: `https://your-app.up.railway.app/webhook/twilio`
3. Send the join code from your phone to the sandbox number once

### 4. Initialize your user

Visit: `https://your-app.up.railway.app/admin/setup?name=YourName`

### 5. Connect Strava

Visit: `https://your-app.up.railway.app/auth/strava`
Complete the OAuth login — Strava will now push runs automatically.

### 6. Connect Google Calendar

Visit: `https://your-app.up.railway.app/auth/google-calendar`
Complete the OAuth login — calendar events will be read for weekly planning.

### 7. Set up Apple Health (iOS Shortcuts)

On your iPhone, create a **Shortcut** with these steps:
1. **Find Health Samples** — type: Weight, date range: last 1 day
2. **Find Health Samples** — type: Sleep Analysis, date range: last 1 day
3. **Get Contents of URL** — method: POST, URL: `https://your-app.up.railway.app/health/shortcut`
   - Body: JSON
   - `api_key`: your HEALTH_SHORTCUT_API_KEY value
   - `weight_kg`: Shortcut Input → weight samples → first item → value
   - `sleep_hours`: Shortcut Input → sleep samples → first item → value (in hours)

4. In **Automation** tab: New Automation → Time of Day → 6:00 AM → run the shortcut → **Don't Ask Before Running**

### 8. Bookmark the dashboard

Visit: `https://your-app.up.railway.app/dashboard`
Add to your iPhone home screen for easy access.

---

## Using the bot

### Set your goals (first time)

Send a message like:
> "Set my goals: 2200 calories, 180g protein, 240g carbs, 65g fat. Water 3 liters, sleep 8 hours. Supplements: creatine 5g morning, vitamin D 2000IU morning."

### Log food

- **Text**: "I had chicken breast 200g, rice 150g, and salad for lunch"
- **Photo**: Send a photo of your meal (caption optional)
- **Voice**: Record a voice note describing what you ate

### Log a workout

- **Voice** (recommended): Record a voice note describing your session
- **Text**: "Did push day — bench press 4x8 at 80kg, OHP 3x10 at 50kg, tricep pushdown 3x15"
- **Strava**: Runs sync automatically after you finish

### Weekly plan

Every Monday morning the bot will ask you for your plan. Reply with something like:
> "Push Monday, Run Tuesday, Pull Wednesday, rest Thursday, Legs Friday, Run Saturday"

### Log water

> "Drank 500ml"
> "2 glasses of water"

### Log weight

> "Weight today 84.5kg"

### Get a summary

> "How did I do today?"
> "Weekly summary"

---

## Project structure

```
fitness-bot/
├── app/                    # Python FastAPI backend
│   ├── models/             # SQLAlchemy database models
│   ├── routers/            # HTTP endpoints
│   ├── services/           # Business logic
│   ├── claude/             # Claude AI prompts and tools
│   └── tasks/              # Celery scheduled tasks
└── dashboard/              # React web dashboard
    └── src/
        ├── pages/          # Daily, Weekly, Trends, Photos
        └── components/     # Reusable UI components
```

## Monthly costs

| Service | Cost |
|---------|------|
| Railway (app + Postgres + Redis) | ~$10 |
| Twilio WhatsApp | ~$3–8 |
| Claude API | ~$5–15 |
| OpenAI Whisper | ~$2–5 |
| Cloudflare R2 | Free |
| **Total** | **~$20–38/month** |
