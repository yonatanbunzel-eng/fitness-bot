import json
from datetime import datetime, timezone, timedelta, date

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.oauth_token import OAuthToken
from app.models.user import User

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"


def get_token(db: Session, user: User) -> OAuthToken | None:
    return (
        db.query(OAuthToken)
        .filter(OAuthToken.user_id == user.id, OAuthToken.service == "google_calendar")
        .first()
    )


async def refresh_access_token(db: Session, token: OAuthToken) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(GOOGLE_TOKEN_URL, data={
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
        })
        resp.raise_for_status()
        data = resp.json()

    token.access_token = data["access_token"]
    token.expires_at = datetime.now(timezone.utc) + timedelta(seconds=data.get("expires_in", 3600))
    db.commit()
    return token.access_token


async def get_valid_access_token(db: Session, user: User) -> str | None:
    token = get_token(db, user)
    if not token:
        return None
    now = datetime.now(timezone.utc)
    if token.expires_at and token.expires_at <= now + timedelta(minutes=5):
        return await refresh_access_token(db, token)
    return token.access_token


async def get_week_events(db: Session, user: User) -> list[dict]:
    """Fetch calendar events for the current week."""
    access_token = await get_valid_access_token(db, user)
    if not access_token:
        return []

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GOOGLE_CALENDAR_API}/calendars/primary/events",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "timeMin": f"{week_start.isoformat()}T00:00:00Z",
                "timeMax": f"{week_end.isoformat()}T00:00:00Z",
                "singleEvents": "true",
                "orderBy": "startTime",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    events = []
    for item in data.get("items", []):
        start = item.get("start", {})
        end = item.get("end", {})
        events.append({
            "title": item.get("summary", "Busy"),
            "start": start.get("dateTime", start.get("date", "")),
            "end": end.get("dateTime", end.get("date", "")),
        })
    return events


def format_busy_blocks_for_prompt(events: list[dict]) -> str:
    if not events:
        return "No calendar events this week."
    lines = []
    for e in events:
        start = e["start"][:16].replace("T", " ") if "T" in e["start"] else e["start"]
        lines.append(f"- {e['title']}: {start}")
    return "\n".join(lines)


def get_calendar_auth_url(redirect_uri: str) -> str:
    from urllib.parse import urlencode
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar.readonly",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


async def exchange_code(code: str, redirect_uri: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(GOOGLE_TOKEN_URL, data={
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        })
        resp.raise_for_status()
        return resp.json()


def save_token(db: Session, user: User, token_data: dict) -> OAuthToken:
    token = get_token(db, user)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600))

    if token:
        token.access_token = token_data["access_token"]
        if token_data.get("refresh_token"):
            token.refresh_token = token_data["refresh_token"]
        token.expires_at = expires_at
    else:
        token = OAuthToken(
            user_id=user.id,
            service="google_calendar",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_at=expires_at,
            scope=token_data.get("scope", ""),
        )
        db.add(token)
    db.commit()
    return token
