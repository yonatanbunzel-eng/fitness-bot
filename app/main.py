import os

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

app = FastAPI(title="Fitness Bot API", docs_url="/docs")

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


# Serve React dashboard static files from /dashboard/dist
dashboard_dist = os.path.join(os.path.dirname(__file__), "..", "dashboard", "dist")
if os.path.exists(dashboard_dist):
    app.mount("/dashboard", StaticFiles(directory=dashboard_dist, html=True), name="dashboard")
