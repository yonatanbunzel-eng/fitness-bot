"""
POST /webhook/twilio
Receives all incoming WhatsApp messages from Twilio.
Detects message type (text / image / audio) and routes accordingly.
"""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import claude_processor, whisper_service, photo_service, twilio_service

router = APIRouter()


@router.post("/webhook/twilio", response_class=PlainTextResponse)
async def twilio_webhook(
    request: Request,
    From: str = Form(default=""),
    Body: str = Form(default=""),
    NumMedia: str = Form(default="0"),
    MediaUrl0: str = Form(default=""),
    MediaContentType0: str = Form(default=""),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.whatsapp_number == From).first()
    if not user:
        return PlainTextResponse("")  # Ignore unknown numbers

    reply = ""

    try:
        num_media = int(NumMedia)

        if num_media > 0 and MediaUrl0:
            media_type = MediaContentType0.lower()
            media_bytes = await twilio_service.download_media(MediaUrl0)

            if "audio" in media_type:
                # Voice message → transcribe → process as text with workout context
                transcript = whisper_service.transcribe_audio(media_bytes)
                reply = claude_processor.process_message(
                    db=db,
                    user=user,
                    text=f"[Voice message transcript]: {transcript}",
                )

            elif "image" in media_type:
                # Photo → check if food or progress photo
                caption = Body.strip() if Body.strip() else None
                category = photo_service.detect_photo_category(caption)

                if category == "food":
                    # Process as food photo → Claude vision
                    reply = claude_processor.process_message(
                        db=db,
                        user=user,
                        image_bytes=media_bytes,
                        image_media_type=media_type,
                        photo_caption=caption or "I just ate this.",
                    )
                    # Save as food photo
                    photo_service.save_progress_photo(
                        db, user, media_bytes,
                        category="food", caption=caption,
                    )
                else:
                    # Progress photo → save + log
                    import re
                    weight_match = re.search(r"(\d{2,3}(?:\.\d)?)\s*(?:kg|קג|ק\"ג)", caption or "", re.IGNORECASE)
                    weight_kg = float(weight_match.group(1)) if weight_match else None

                    photo_service.save_progress_photo(
                        db, user, media_bytes,
                        category=category, caption=caption, weight_kg=weight_kg,
                    )
                    from datetime import datetime, timezone
                    now = datetime.now(timezone.utc)
                    iso_week = now.isocalendar()
                    reply = f"Photo saved! Week {iso_week.week}/{iso_week.year} — category: {category}."
                    if weight_kg:
                        from app.models.weight_log import WeightLog
                        db.add(WeightLog(user_id=user.id, weight_kg=weight_kg, source="photo_check_in"))
                        db.commit()
                        reply += f"\nWeight logged: {weight_kg}kg."

            else:
                reply = "Got a file I can't process yet. Send text, a photo, or a voice message!"

        else:
            # Pure text message
            text = Body.strip()
            if text:
                reply = claude_processor.process_message(db=db, user=user, text=text)

    except Exception as e:
        reply = "Something went wrong on my end. Try again in a moment!"
        # In production, log the error
        import traceback
        traceback.print_exc()

    if reply:
        twilio_service.send_message(From, reply)

    return PlainTextResponse("")  # Twilio expects empty 200 response
