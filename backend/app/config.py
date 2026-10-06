"""Environment-backed application configuration."""

import os


def _env_bool(name: str, default: bool) -> bool:
    """Read a conventional boolean environment variable."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


ENABLE_DEV_ENDPOINTS = _env_bool("ENABLE_DEV_ENDPOINTS", True)
AUTO_SEED = _env_bool("AUTO_SEED", False)
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)
