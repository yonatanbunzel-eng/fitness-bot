import os
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import (
    webhook_twilio,
    webhook_strava,
    auth_strava,
    auth_calendar,
    health_shortcut,
    api_dashboard,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background scheduler when app starts."""
    scheduler_task = asyncio.create_task(_run_scheduler())
    yield
    scheduler_task.cancel()


async def _run_scheduler():
    """
    Lightweight in-process scheduler — replaces Celery for free-tier hosting.
    Checks every minute whether a scheduled task should fire.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from app.config import settings

    tz = ZoneInfo(settings.user_timezone)
    last_daily = None
    last_weekly_plan = None
    last_weekly_review = None

    while True:
        try:
            await asyncio.sleep(60)
            now = datetime.now(tz)
            today_key = now.strftime("%Y-%m-%d")

            # Daily summary — 20:00 every day
            if now.hour == 20 and now.minute == 0 and last_daily != today_key:
                last_daily = today_key
                from app.tasks.daily_summary import send_daily_summary
                await asyncio.to_thread(send_daily_summary)

            # Weekly plan prompt — Monday 07:00
            week_key = now.strftime("%Y-W%W")
            if now.weekday() == 0 and now.hour == 7 and now.minute == 0 and last_weekly_plan != week_key:
                last_weekly_plan = week_key
                from app.tasks.weekly_plan import prompt_weekly_plan
                await asyncio.to_thread(prompt_weekly_plan)

            # Weekly review — Sunday 20:00
            if now.weekday() == 6 and now.hour == 20 and now.minute == 0 and last_weekly_review != week_key:
                last_weekly_review = week_key
                from app.tasks.weekly_review import send_weekly_review
                await asyncio.to_thread(send_weekly_review)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")


app = FastAPI(title="Fitness Bot API", docs_url="/docs", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_twilio.router)
app.include_router(webhook_strava.router)
app.include_router(auth_strava.router)
app.include_router(auth_calendar.router)
app.include_router(health_shortcut.router)
app.include_router(api_dashboard.router)


@app.get("/admin/setup")
def admin_setup(name: str = Query(default="")):
    """One-time endpoint to create the user in the database."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.config import settings

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.whatsapp_number == settings.user_whatsapp_number).first()
        if existing:
            return {"status": "already exists", "user": existing.name}
        user = User(
            whatsapp_number=settings.user_whatsapp_number,
            name=name or settings.user_name,
            timezone=settings.user_timezone,
        )
        db.add(user)
        db.commit()
        return {"status": "created", "user": user.name, "id": str(user.id)}
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ping")
def ping():
    """Keep-alive endpoint — pinged every 10 min by cron-job.org to prevent sleep."""
    return "pong"


# Serve React dashboard static files from /dashboard/dist
dashboard_dist = os.path.join(os.path.dirname(__file__), "..", "dashboard", "dist")
if os.path.exists(dashboard_dist):
    app.mount("/dashboard", StaticFiles(directory=dashboard_dist, html=True), name="dashboard")
