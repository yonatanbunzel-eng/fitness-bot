import json

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services import strava_service, workout_service, twilio_service
from app.claude.context_builder import get_current_weekly_plan
from app.services.workout_service import mark_plan_session_complete

router = APIRouter()


@router.get("/webhook/strava")
async def strava_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.strava_verify_token:
        return JSONResponse({"hub.challenge": hub_challenge})
    return JSONResponse({"error": "invalid"}, status_code=403)


@router.post("/webhook/strava")
async def strava_event(request: Request, db: Session = Depends(get_db)):
    body = await request.json()

    object_type = body.get("object_type")
    aspect_type = body.get("aspect_type")
    activity_id = body.get("object_id")
    owner_id = str(body.get("owner_id", ""))

    if object_type != "activity" or aspect_type != "create":
        return JSONResponse({"status": "ignored"})

    # Find user by Strava athlete ID stored in extra field
    from app.models.oauth_token import OAuthToken
    token = (
        db.query(OAuthToken)
        .filter(OAuthToken.service == "strava")
        .all()
    )
    user = None
    for t in token:
        try:
            extra = json.loads(t.extra or "{}")
            if str(extra.get("athlete_id")) == owner_id:
                user = db.query(User).filter(User.id == t.user_id).first()
                break
        except Exception:
            continue

    if not user:
        return JSONResponse({"status": "user not found"})

    try:
        activity = await strava_service.fetch_activity(db, user, activity_id)
        log = workout_service.create_from_strava(db, user, activity)

        weekly_plan = get_current_weekly_plan(db, user)
        mark_plan_session_complete(db, log, weekly_plan)

        # Build proactive WhatsApp notification
        dist = log.distance_km or 0
        dur = log.duration_minutes or 0
        pace = log.pace_min_per_km or 0
        pace_str = f"{int(pace)}:{int((pace % 1) * 60):02d}/km" if pace else ""

        msg = f"Run synced from Strava!\n{dist:.1f}km in {dur}min"
        if pace_str:
            msg += f" ({pace_str})"

        # Check weekly run progress
        from app.claude.context_builder import get_active_goal
        from app.models.workout_log import WorkoutLog
        from datetime import date, timedelta
        goal = get_active_goal(db, user)
        if goal and goal.weekly_run_km > 0:
            week_start = date.today() - timedelta(days=date.today().weekday())
            week_runs = (
                db.query(WorkoutLog)
                .filter(
                    WorkoutLog.user_id == user.id,
                    WorkoutLog.workout_type == "run",
                    WorkoutLog.workout_date >= week_start,
                )
                .all()
            )
            total_km = sum(w.distance_km or 0 for w in week_runs)
            pct = int((total_km / goal.weekly_run_km) * 100)
            msg += f"\n\nWeekly run goal: {total_km:.1f}/{goal.weekly_run_km:.0f}km ({pct}%)"

        twilio_service.send_to_user(msg)

    except Exception:
        import traceback
        traceback.print_exc()

    return JSONResponse({"status": "ok"})
