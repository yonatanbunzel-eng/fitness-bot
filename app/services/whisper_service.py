import io
import tempfile
import os

from openai import OpenAI

from app.config import settings

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.ogg") -> str:
    """
    Transcribe audio bytes (OGG Opus from WhatsApp).
    Converts OGG → WAV via pydub+ffmpeg before sending to Whisper.
    """
    from pydub import AudioSegment

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ogg_file:
        ogg_file.write(audio_bytes)
        ogg_path = ogg_file.name

    wav_path = ogg_path.replace(".ogg", ".wav")
    try:
        audio = AudioSegment.from_ogg(ogg_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_path, format="wav")

        with open(wav_path, "rb") as wav_file:
            response = get_client().audio.transcriptions.create(
                model="whisper-1",
                file=wav_file,
                language="he",  # Primary language is Hebrew; Whisper auto-detects anyway
            )
        return response.text
    finally:
        if os.path.exists(ogg_path):
            os.unlink(ogg_path)
        if os.path.exists(wav_path):
            os.unlink(wav_path)
