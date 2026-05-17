from app.tasks.celery_app import celery


@celery.task(name="app.tasks.weekly_plan.prompt_weekly_plan")
def prompt_weekly_plan():
    from app.database import SessionLocal
    from app.config import settings
    from app.models.user import User
    from app.services import calendar_service, twilio_service
    from app.claude.context_builder import get_active_goal
    import asyncio

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.whatsapp_number == settings.user_whatsapp_number).first()
        if not user:
            return

        goal = get_active_goal(db, user)
        default_split = goal.weekly_training_split if goal else {}

        try:
            events = asyncio.run(calendar_service.get_week_events(db, user))
            busy_str = calendar_service.format_busy_blocks_for_prompt(events)
        except Exception:
            busy_str = ""

        lines = ["🗓️ שבוע חדש מתחיל! מה תוכנית האימונים שלך השבוע?"]

        if default_split:
            split_str = ", ".join(f"{v} — {k}" for k, v in default_split.items())
            lines.append(f"\nחלוקה רגילה: {split_str}")

        if busy_str and busy_str != "No calendar events this week.":
            lines.append(f"\nאירועים ביומן השבוע:\n{busy_str}")

        lines.append(
            "\nפשוט שלח לי את התוכנית, לדוגמה:\n"
            "\"דחיפה ב׳, ריצה ג׳, משיכה ד׳, מנוחה ה׳, רגליים ו׳, ריצה ש׳\""
        )

        twilio_service.send_to_user("\n".join(lines))
    finally:
        db.close()
