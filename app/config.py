from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://fitness:fitness@localhost:5432/fitness_bot"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    openai_api_key: str = ""

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = "whatsapp:+14155238886"
    user_whatsapp_number: str = ""

    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "fitness-photos"
    r2_public_url: str = ""

    strava_client_id: str = ""
    strava_client_secret: str = ""
    strava_verify_token: str = "fitness_bot_strava_verify"

    google_client_id: str = ""
    google_client_secret: str = ""

    health_shortcut_api_key: str = ""
    dashboard_api_key: str = ""

    app_base_url: str = "http://localhost:8000"
    user_name: str = "User"
    user_timezone: str = "Asia/Jerusalem"


settings = Settings()
