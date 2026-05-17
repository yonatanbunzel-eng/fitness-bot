from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.user import User


def get_current_user(db: Session = Depends(get_db)) -> User:
    """Single-user app — always returns the one user from config."""
    user = db.query(User).filter(User.whatsapp_number == settings.user_whatsapp_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not initialized. Run /admin/setup first.")
    return user


def verify_dashboard_key(x_api_key: str = Header(None)) -> None:
    if x_api_key != settings.dashboard_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
