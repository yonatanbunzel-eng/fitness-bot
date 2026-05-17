"""
Central orchestration: receives a parsed WhatsApp message, calls Claude,
dispatches the tool_use result to the appropriate service, returns a reply string.
"""
import base64
from datetime import date, datetime, timezone

import anthropic
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.claude.tools import TOOLS
from app.claude.system_prompt import build_system_prompt
from app.claude.context_builder import (
    get_active_goal,
    get_today_nutrition_totals,
    get_today_water_ml,
    get_today_workout_summaries,
    get_current_weekly_plan,
    format_weekly_plan_summary,
    get_conversation_history,
    append_to_conversation,
)

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _build_user_message(
    text: str | None,
    image_bytes: bytes | None = None,
    image_media_type: str = "image/jpeg",
) -> list[dict]:
    """Assemble a Claude user message content block."""
    content = []
    if image_bytes:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_media_type,
                "data": base64.standard_b64encode(image_bytes).decode("utf-8"),
            },
        })
    if text:
        content.append({"type": "text", "text": text})
    return content


def process_message(
    db: Session,
    user: User,
    text: str | None = None,
    image_bytes: bytes | None = None,
    image_media_type: str = "image/jpeg",
    photo_caption: str | None = None,
) -> str:
    """
    Main entry point. Call with text, image, or both.
    Returns the reply string to send via WhatsApp.
    """
    goal = get_active_goal(db, user)
    nutrition = get_today_nutrition_totals(db, user)
    water = get_today_water_ml(db, user)
    workouts = get_today_workout_summaries(db, user)
    weekly_plan = get_current_weekly_plan(db, user)
    plan_summary = format_weekly_plan_summary(weekly_plan)
    history = get_conversation_history(db, user)

    system_blocks = build_system_prompt(
        today_calories=nutrition["calories"],
        today_protein=nutrition["protein_g"],
        today_carbs=nutrition["carbs_g"],
        today_fat=nutrition["fat_g"],
        today_water_ml=water,
        today_workouts=workouts,
        goal_calories=goal.calories_target if goal else 2000,
        goal_protein=goal.protein_g if goal else 150,
        goal_carbs=goal.carbs_g if goal else 200,
        goal_fat=goal.fat_g if goal else 70,
        goal_water_ml=goal.water_ml if goal else 3000,
        goal_sleep_hours=goal.sleep_hours if goal else 8.0,
        supplements=goal.supplements if goal else [],
        weekly_plan_summary=plan_summary,
        user_name=user.name,
    )

    # Build message list: history + current message
    messages = list(history)
    user_content = _build_user_message(
        text=photo_caption or text,
        image_bytes=image_bytes,
        image_media_type=image_media_type,
    )
    messages.append({"role": "user", "content": user_content})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_blocks,
        tools=TOOLS,
        messages=messages,
    )

    reply = _dispatch_tool_use(db, user, response, weekly_plan)

    # Store conversation turn
    user_text_for_history = photo_caption or text or "[image]"
    append_to_conversation(db, user, "user", user_text_for_history)
    append_to_conversation(db, user, "assistant", reply)

    return reply


def _dispatch_tool_use(db: Session, user: User, response, weekly_plan) -> str:
    """Extract tool_use from Claude response and call the right service."""
    from app.services import (
        nutrition_service,
        workout_service,
        goal_service,
        schedule_service,
    )

    for block in response.content:
        if block.type != "tool_use":
            continue

        name = block.name
        inp = block.input

        if name == "log_food":
            nutrition_service.create_log(db, user, inp)
            return inp.get("reply_message", "Logged!")

        elif name == "log_workout":
            workout_service.create_log(db, user, inp)
            # If off-plan and we have a weekly plan, trigger adaptation
            if inp.get("plan_adherence") == "off_plan" and weekly_plan:
                schedule_service.record_adaptation(
                    db, weekly_plan,
                    date.fromisoformat(inp["workout_date"]),
                    inp.get("adherence_note", "Off-plan workout"),
                    inp.get("workout_type", ""),
                )
            return inp.get("reply_message", "Workout logged!")

        elif name == "log_water":
            from app.models.water_log import WaterLog
            log = WaterLog(user_id=user.id, amount_ml=inp["amount_ml"])
            db.add(log)
            db.commit()
            return inp.get("reply_message", "Water logged!")

        elif name == "log_weight":
            from app.models.weight_log import WeightLog
            log = WeightLog(
                user_id=user.id,
                weight_kg=inp["weight_kg"],
                source="manual",
                notes=inp.get("notes"),
            )
            db.add(log)
            db.commit()
            return inp.get("reply_message", "Weight logged!")

        elif name == "log_sleep":
            from app.models.sleep_log import SleepLog
            log = SleepLog(
                user_id=user.id,
                date=date.today(),
                duration_hours=inp["duration_hours"],
                quality_score=inp.get("quality_score"),
                source="manual",
            )
            db.add(log)
            db.commit()
            return inp.get("reply_message", "Sleep logged!")

        elif name == "set_weekly_plan":
            schedule_service.set_weekly_plan(db, user, inp)
            return inp.get("reply_message", "Weekly plan set!")

        elif name == "adapt_weekly_plan":
            if weekly_plan:
                schedule_service.apply_adaptation(db, weekly_plan, inp)
            return inp.get("reply_message", "Plan adapted!")

        elif name == "set_goals":
            goal_service.update_goals(db, user, inp)
            return inp.get("reply_message", "Goals updated!")

        elif name == "send_summary":
            return inp.get("reply_message", "")

        elif name == "chat_reply":
            return inp.get("reply_message", "")

    # Fallback: extract text response if no tool_use
    for block in response.content:
        if hasattr(block, "text"):
            return block.text

    return "Got it!"
