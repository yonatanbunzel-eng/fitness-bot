from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import calendar_service

router = APIRouter()


@router.get("/auth/google-calendar")
async def google_calendar_auth(user: User = Depends(get_current_user)):
    redirect_uri = f"{settings.app_base_url}/auth/google-calendar/callback"
    url = calendar_service.get_calendar_auth_url(redirect_uri)
    return RedirectResponse(url)


@router.get("/auth/google-calendar/callback")
async def google_calendar_callback(
    code: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    redirect_uri = f"{settings.app_base_url}/auth/google-calendar/callback"
    token_data = await calendar_service.exchange_code(code, redirect_uri)
    calendar_service.save_token(db, user, token_data)
    return {"status": "Google Calendar connected!"}
