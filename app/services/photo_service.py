import io
import uuid
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from PIL import Image

from app.config import settings
from app.models.progress_photo import ProgressPhoto
from app.models.user import User
from sqlalchemy.orm import Session


def _get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def upload_photo(image_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> str:
    """Upload to R2 and return the public URL."""
    r2 = _get_r2_client()
    r2.put_object(
        Bucket=settings.r2_bucket_name,
        Key=filename,
        Body=image_bytes,
        ContentType=content_type,
    )
    return f"{settings.r2_public_url}/{filename}"


def create_thumbnail(image_bytes: bytes, max_size: tuple = (400, 400)) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail(max_size, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    return buf.getvalue()


def save_progress_photo(
    db: Session,
    user: User,
    image_bytes: bytes,
    category: str = "front",
    caption: str | None = None,
    weight_kg: float | None = None,
) -> ProgressPhoto:
    now = datetime.now(timezone.utc)
    iso_week = now.isocalendar()
    file_id = str(uuid.uuid4())[:8]
    filename = f"photos/{user.id}/{iso_week.year}/w{iso_week.week}/{file_id}.jpg"
    thumb_filename = f"photos/{user.id}/{iso_week.year}/w{iso_week.week}/{file_id}_thumb.jpg"

    storage_url = upload_photo(image_bytes, filename)
    thumbnail_bytes = create_thumbnail(image_bytes)
    thumbnail_url = upload_photo(thumbnail_bytes, thumb_filename)

    photo = ProgressPhoto(
        user_id=user.id,
        taken_at=now,
        week_number=iso_week.week,
        year=iso_week.year,
        category=category,
        storage_url=storage_url,
        thumbnail_url=thumbnail_url,
        weight_kg=weight_kg,
        caption=caption,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def detect_photo_category(caption: str | None) -> str:
    """Simple keyword-based category detection from caption."""
    if not caption:
        return "front"
    caption_lower = caption.lower()
    if any(w in caption_lower for w in ["אוכל", "food", "אכלתי", "ארוחה", "meal"]):
        return "food"
    if any(w in caption_lower for w in ["משקל", "weight", "שוקל", "קג", "kg"]):
        return "weight_checkin"
    if any(w in caption_lower for w in ["צד", "side"]):
        return "side"
    if any(w in caption_lower for w in ["אחורי", "back"]):
        return "back"
    return "front"
