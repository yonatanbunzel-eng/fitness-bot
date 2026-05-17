import httpx
from twilio.rest import Client

from app.config import settings

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return _client


def send_message(to: str, body: str) -> None:
    client = get_client()
    client.messages.create(
        from_=settings.twilio_whatsapp_number,
        to=to,
        body=body,
    )


def send_to_user(body: str) -> None:
    send_message(settings.user_whatsapp_number, body)


async def download_media(media_url: str) -> bytes:
    """Download a Twilio media file (requires Basic Auth)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            media_url,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.content
