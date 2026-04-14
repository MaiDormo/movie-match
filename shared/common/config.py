# shared/common/config.py
import os
from typing import List


def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def get_cors_origins(default: str = "*") -> List[str]:
    raw = os.getenv("CORS_ORIGINS", default)
    # Supports: "http://a,http://b"
    return [origin.strip() for origin in raw.split(",") if origin.strip()]