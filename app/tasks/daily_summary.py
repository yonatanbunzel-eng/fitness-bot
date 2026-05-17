from app.tasks.celery_app import celery


@celery.task(name="app.tasks.daily_summary.send_daily_summary")
def send_daily_summary():
    from app.database import SessionLocal
    from app.config import settings
    from app.models.user import User
    from app.claude.context_builder import (
        get_active_goal,
        get_today_nutrition_totals,
        get_today_water_ml,
        get_today_workout_summaries,
        get_current_weekly_plan,
    )
    from app.services.twilio_service import send_to_user
    from app.models.sleep_log import SleepLog
    from datetime import date

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.whatsapp_number == settings.user_whatsapp_number).first()
        if not user:
            return

        goal = get_active_goal(db, user)
        nutrition = get_today_nutrition_totals(db, user)
        water = get_today_water_ml(db, user)
        workouts = get_today_workout_summaries(db, user)
        weekly_plan = get_current_weekly_plan(db, user)

        sleep = db.query(SleepLog).filter(
            SleepLog.user_id == user.id, SleepLog.date == date.today()
        ).first()

        cal_target = goal.calories_target if goal else 2000
        cal_eaten = nutrition["calories"]
        cal_pct = int((cal_eaten / cal_target) * 100) if cal_target else 0

        water_target = goal.water_ml if goal else 3000
        water_pct = int((water / water_target) * 100) if water_target else 0

        cal_emoji = "✅" if 90 <= cal_pct <= 110 else ("⚠️" if cal_pct < 80 or cal_pct > 130 else "🟡")
        water_emoji = "✅" if water_pct >= 90 else "💧"

        lines = [f"📊 סיכום יומי — {date.today().strftime('%d.%m.%Y')}"]
        lines.append(f"\n{cal_emoji} קלוריות: {cal_eaten}/{cal_target} ({cal_pct}%)")
        lines.append(f"  חלבון: {nutrition['protein_g']:.0f}g / {goal.protein_g if goal else 150}g")
        lines.append(f"\n{water_emoji} מים: {water}מ״ל / {water_target}מ״ל ({water_pct}%)")

        if sleep:
            sleep_target = goal.sleep_hours if goal else 8.0
            sleep_emoji = "✅" if sleep.duration_hours >= sleep_target - 0.5 else "😴"
            lines.append(f"\n{sleep_emoji} שינה: {sleep.duration_hours:.1f} שעות")

        if workouts:
            lines.append(f"\n💪 אימונים: {', '.join(workouts)}")
        else:
            if weekly_plan:
                today_day = date.today().strftime("%A").lower()
                session = (weekly_plan.planned_sessions or {}).get(today_day)
                if session and not session.get("rest"):
                    lines.append(f"\n⚡ לא נרשם אימון היום (מתוכנן: {session.get('type', 'אימון')})")

        send_to_user("\n".join(lines))
    finally:
        db.close()
