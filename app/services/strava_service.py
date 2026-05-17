import json
from datetime import datetime, timezone, timedelta

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.oauth_token import OAuthToken
from app.models.user import User

STRAVA_API_BASE = "https://www.strava.com/api/v3"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"


def get_token(db: Session, user: User) -> OAuthToken | None:
    return (
        db.query(OAuthToken)
        .filter(OAuthToken.user_id == user.id, OAuthToken.service == "strava")
        .first()
    )


async def refresh_access_token(db: Session, token: OAuthToken) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(STRAVA_TOKEN_URL, data={
            "client_id": settings.strava_client_id,
            "client_secret": settings.strava_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
        })
        resp.raise_for_status()
        data = resp.json()

    token.access_token = data["access_token"]
    token.refresh_token = data.get("refresh_token", token.refresh_token)
    token.expires_at = datetime.fromtimestamp(data["expires_at"], tz=timezone.utc)
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


async def fetch_activity(db: Session, user: User, activity_id: int) -> dict:
    access_token = await get_valid_access_token(db, user)
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{STRAVA_API_BASE}/activities/{activity_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()


def get_strava_auth_url(redirect_uri: str) -> str:
    return (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={settings.strava_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=activity:read_all"
    )


async def exchange_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(STRAVA_TOKEN_URL, data={
            "client_id": settings.strava_client_id,
            "client_secret": settings.strava_client_secret,
            "code": code,
            "grant_type": "authorization_code",
        })
        resp.raise_for_status()
        return resp.json()


def save_token(db: Session, user: User, token_data: dict) -> OAuthToken:
    extra = {"athlete_id": token_data.get("athlete", {}).get("id")}
    token = get_token(db, user)
    if token:
        token.access_token = token_data["access_token"]
        token.refresh_token = token_data.get("refresh_token")
        token.expires_at = datetime.fromtimestamp(token_data["expires_at"], tz=timezone.utc)
        token.extra = json.dumps(extra)
    else:
        token = OAuthToken(
            user_id=user.id,
            service="strava",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_at=datetime.fromtimestamp(token_data["expires_at"], tz=timezone.utc),
            scope=token_data.get("scope", ""),
            extra=json.dumps(extra),
        )
        db.add(token)
    db.commit()
    return token
