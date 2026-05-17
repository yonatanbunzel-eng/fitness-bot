from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.config import settings


STATIC_PERSONA = """אתה מאמן כושר ותזונה אישי שמתקשר דרך וואטסאפ בעברית.
אתה מעודד, קצר לעניין וספציפי. הודעות וואטסאפ חייבות להיות קצרות — עד 6 שורות, אלא אם המשתמש ביקש פירוט.
תמיד תענה בעברית, גם אם השאלה מגיעה באנגלית.

כללים:
- תמיד השתמש בכלי (tool) כשיש נתונים לרשום. אל תאשר בלי לרשום.
- השתמש ב-log_food לכל אזכור של אוכל/ארוחה.
- השתמש ב-log_workout לכל אזכור של אימון/פעילות גופנית.
- השתמש ב-chat_reply רק לשאלות ועצות ללא נתונים לרשום.
- בהערכת אוכל מתמונות: תן טווח קלוריות, ציין רמת ביטחון, הצע חלופות אם חרגו מהתפריט.
- בניתוח הקלטות קוליות: חלץ שמות תרגילים, סטים, חזרות ומשקלים. תרגם שמות עבריים לאנגלית לצורך אחסון.
- תוספי תזונה: קריאטין=creatine, חלבון=protein, ויטמין=vitamin, אומגה=omega.
- השתמש באמוג׳י במשורה (1-2 לכל הודעה לכל היותר).
- אל תמציא מספרים שאתה לא בטוח בהם — השתמש בטווחים וציין אי-וודאות.
- כשמשתמש שולח תמונת התקדמות (גוף, משקל) — שמור אותה ואשר בקצרה.
- אם המשתמש חרג מהתפריט — אל תשפוט, הצע איך להשלים את היום.
"""


def build_system_prompt(
    today_calories: int = 0,
    today_protein: float = 0,
    today_carbs: float = 0,
    today_fat: float = 0,
    today_water_ml: int = 0,
    today_workouts: list[str] | None = None,
    goal_calories: int = 2000,
    goal_protein: float = 150,
    goal_carbs: float = 200,
    goal_fat: float = 70,
    goal_water_ml: int = 3000,
    goal_sleep_hours: float = 8.0,
    supplements: list[dict] | None = None,
    weekly_plan_summary: str = "",
    user_name: str = "User",
) -> list[dict]:
    """Returns a list of system blocks for the Anthropic API (supports prompt caching)."""
    DAYS_HE = {
        "monday": "יום שני", "tuesday": "יום שלישי", "wednesday": "יום רביעי",
        "thursday": "יום חמישי", "friday": "יום שישי", "saturday": "שבת", "sunday": "יום ראשון",
    }

    tz = ZoneInfo(settings.user_timezone)
    now = datetime.now(tz)
    day_en = now.strftime("%A").lower()
    day_he = DAYS_HE.get(day_en, day_en)
    today_str = now.strftime(f"{day_he}, %d.%m.%Y")

    calories_remaining = goal_calories - today_calories
    protein_remaining = goal_protein - today_protein

    workouts_str = ", ".join(today_workouts) if today_workouts else "לא נרשם עדיין"

    supplements_str = ""
    if supplements:
        supp_list = [f"{s['name']} {s.get('dose', '')} ({s.get('timing', '')})" for s in supplements]
        supplements_str = "תוספים: " + ", ".join(supp_list)

    live_context = f"""## משתמש: {user_name} | היום: {today_str}

## יעדים יומיים:
- קלוריות: {goal_calories} | חלבון: {goal_protein}g | פחמימות: {goal_carbs}g | שומן: {goal_fat}g
- מים: {goal_water_ml}מ״ל | שינה: {goal_sleep_hours} שעות
{supplements_str}

## התקדמות היום:
- אכל: {today_calories} קלוריות ({today_protein:.0f}g חלבון / {today_carbs:.0f}g פחמימות / {today_fat:.0f}g שומן)
- נותר: {calories_remaining} קלוריות | {protein_remaining:.0f}g חלבון
- מים: {today_water_ml}מ״ל / {goal_water_ml}מ״ל
- אימונים היום: {workouts_str}

## תוכנית השבוע (היום {day_he}):
{weekly_plan_summary if weekly_plan_summary else "לא נקבעה תוכנית שבועית עדיין. בקש מהמשתמש לקבוע."}
"""

    return [
        {
            "type": "text",
            "text": STATIC_PERSONA,
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": live_context,
        },
    ]
