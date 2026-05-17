from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import strava_service

router = APIRouter()


@router.get("/auth/strava")
async def strava_auth(user: User = Depends(get_current_user)):
    redirect_uri = f"{settings.app_base_url}/auth/strava/callback"
    url = strava_service.get_strava_auth_url(redirect_uri)
    return RedirectResponse(url)


@router.get("/auth/strava/callback")
async def strava_callback(
    code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    token_data = await strava_service.exchange_code(code)
    strava_service.save_token(db, user, token_data)

    # Subscribe to Strava webhooks
    await _subscribe_strava_webhook()

    return {"status": "Strava connected!", "athlete": token_data.get("athlete", {}).get("firstname")}


async def _subscribe_strava_webhook():
    import httpx
    callback_url = f"{settings.app_base_url}/webhook/strava"
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "https://www.strava.com/api/v3/push_subscriptions",
                data={
                    "client_id": settings.strava_client_id,
                    "client_secret": settings.strava_client_secret,
                    "callback_url": callback_url,
                    "verify_token": settings.strava_verify_token,
                },
            )
        except Exception:
            pass  # May already be subscribed
