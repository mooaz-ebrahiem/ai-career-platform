import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

def _setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, "").strip()
    return value or default


DATABASE_URL = _setting(
    "DATABASE_URL",
    f"sqlite:///{(PROJECT_ROOT / 'career_platform.db').as_posix()}",
)
JWT_SECRET_KEY = _setting("SECRET_KEY")
if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
    raise RuntimeError(
        "SECRET_KEY is missing or too short in .env (use at least 32 characters). "
        'Generate one: python -c "import secrets; print(secrets.token_urlsafe(48))"'
    )
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(_setting("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
HUGGINGFACE_TOKEN = _setting("HUGGINGFACE_TOKEN")
HF_MODEL = _setting("HF_MODEL", "Qwen/Qwen3-4B-Instruct-2507")
CORS_ORIGINS = tuple(
    origin.strip()
    for origin in (_setting(
        "CORS_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500",
    ) or "").split(",")
    if origin.strip()
)