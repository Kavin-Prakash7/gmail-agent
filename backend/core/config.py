from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    project_name: str = "Flowzint AI Gmail System"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"
    frontend_url: str = "http://localhost:3000"
    gemini_api_key: str = ""

    model_config = ConfigDict(
        env_file=ENV_FILE,
        extra="ignore"
    )

settings = Settings()
