from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery = Celery(
    "fitness_bot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.daily_summary",
        "app.tasks.weekly_plan",
        "app.tasks.weekly_review",
    ],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=settings.user_timezone,
    enable_utc=True,
    beat_schedule={
        # Daily summary at 8 PM user timezone
        "daily-summary": {
            "task": "app.tasks.daily_summary.send_daily_summary",
            "schedule": crontab(hour=20, minute=0),
        },
        # Monday 7 AM — ask user for weekly plan
        "weekly-plan-prompt": {
            "task": "app.tasks.weekly_plan.prompt_weekly_plan",
            "schedule": crontab(hour=7, minute=0, day_of_week=1),
        },
        # Sunday 8 PM — weekly review
        "weekly-review": {
            "task": "app.tasks.weekly_review.send_weekly_review",
            "schedule": crontab(hour=20, minute=0, day_of_week=0),
        },
    },
)
