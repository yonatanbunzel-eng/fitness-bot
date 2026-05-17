from app.tasks.celery_app import celery


@celery.task(name="app.tasks.weekly_review.send_weekly_review")
def send_weekly_review():
    from app.database import SessionLocal
    from app.config import settings
    from app.models.user import User
    from app.services import twilio_service
    from app.services.schedule_service import get_week_start, calculate_completion_rate
    from app.claude.context_builder import get_active_goal, get_current_weekly_plan
    from app.models.workout_log import WorkoutLog
    from app.models.nutrition_log import NutritionLog
    from app.models.weight_log import WeightLog
    from datetime import date, timedelta
    from sqlalchemy import func

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.whatsapp_number == settings.user_whatsapp_number).first()
        if not user:
            return

        goal = get_active_goal(db, user)
        weekly_plan = get_current_weekly_plan(db, user)
        week_start = get_week_start()
        week_end = week_start + timedelta(days=7)

        completion_rate = calculate_completion_rate(weekly_plan) if weekly_plan else 0
        completion_pct = int(completion_rate * 100)
        workouts_this_week = (
            db.query(WorkoutLog)
            .filter(WorkoutLog.user_id == user.id, WorkoutLog.workout_date >= week_start)
            .all()
        )

        daily_cals = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            cals = (
                db.query(func.sum(NutritionLog.calories))
                .filter(NutritionLog.user_id == user.id, NutritionLog.logged_at >= day,
                        NutritionLog.logged_at < day + timedelta(days=1))
                .scalar() or 0
            )
            if cals > 0:
                daily_cals.append(cals)

        avg_cals = int(sum(daily_cals) / len(daily_cals)) if daily_cals else 0

        weights = (
            db.query(WeightLog)
            .filter(WeightLog.user_id == user.id, WeightLog.logged_at >= week_start)
            .order_by(WeightLog.logged_at)
            .all()
        )
        weight_change_str = ""
        if len(weights) >= 2:
            change = weights[-1].weight_kg - weights[0].weight_kg
            sign = "+" if change > 0 else ""
            weight_change_str = f"\nמשקל: {sign}{change:.1f}ק״ג השבוע ({weights[-1].weight_kg}ק״ג)"

        runs = [w for w in workouts_this_week if w.workout_type == "run"]
        run_km = sum(w.distance_km or 0 for w in runs)
        run_str = f"{run_km:.1f}ק״מ ב-{len(runs)} ריצות" if runs else "ריצות: לא"

        lines = ["📅 סיכום שבועי"]
        lines.append(f"\n💪 אימונים: {len(workouts_this_week)} סשנים ({completion_pct}% מהתוכנית)")
        lines.append(f"🏃 ריצה: {run_str}")
        if avg_cals:
            lines.append(f"🥗 ממוצע קלוריות: {avg_cals} ליום")
        if weight_change_str:
            lines.append(weight_change_str)

        if completion_pct >= 80:
            lines.append("\n🔥 שבוע מעולה! כך ממשיכים.")
        elif completion_pct >= 50:
            lines.append("\n👍 מאמץ טוב. בשבוע הבא נעלה.")
        else:
            lines.append("\n💡 שבוע קשה — כל אימון חשוב. ביום שני מתחילים מחדש!")

        if weekly_plan:
            weekly_plan.completion_rate = completion_rate
            db.commit()

        twilio_service.send_to_user("\n".join(lines))
    finally:
        db.close()
