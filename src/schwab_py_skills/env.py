"""Environment loading for Schwab credentials.

Uppercase names are the public interface for this project. Lowercase names are
accepted as compatibility fallbacks for older schwab-py-extra utilities.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class SchwabEnvError(RuntimeError):
    """Raised when required Schwab environment is missing or invalid."""


@dataclass(frozen=True)
class SchwabCredentials:
    api_key: str
    app_secret: str
    callback_url: str
    token_path: Path


ENV_VARS: tuple[str, ...] = (
    "SCHWAB_API_KEY",
    "SCHWAB_APP_SECRET",
    "SCHWAB_CALLBACK_URL",
    "SCHWAB_TOKEN_PATH",
)

LOWERCASE_FALLBACKS = {
    "SCHWAB_API_KEY": "schwab_api_key",
    "SCHWAB_APP_SECRET": "schwab_app_secret",
    "SCHWAB_CALLBACK_URL": "schwab_callback_url",
    "SCHWAB_TOKEN_PATH": "schwab_token_path",
}


def read_env_value(name: str) -> str | None:
    """Read uppercase env value, then lowercase fallback."""

    value = os.getenv(name)
    if value:
        return value
    fallback = LOWERCASE_FALLBACKS[name]
    return os.getenv(fallback) or None


def load_schwab_credentials(*, require_token_exists: bool = False) -> SchwabCredentials:
    """Load required Schwab credentials without inventing defaults."""

    values = {name: read_env_value(name) for name in ENV_VARS}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise SchwabEnvError("Missing required environment variables: " + ", ".join(missing))

    token_path = Path(values["SCHWAB_TOKEN_PATH"]).expanduser()
    if not str(token_path):
        raise SchwabEnvError("SCHWAB_TOKEN_PATH is required and cannot be blank")
    if require_token_exists and not token_path.exists():
        raise SchwabEnvError(f"SCHWAB_TOKEN_PATH does not exist: {token_path}")

    return SchwabCredentials(
        api_key=values["SCHWAB_API_KEY"],
        app_secret=values["SCHWAB_APP_SECRET"],
        callback_url=values["SCHWAB_CALLBACK_URL"],
        token_path=token_path,
    )


def redacted(value: str | None, *, keep: int = 4) -> str:
    if not value:
        return "<missing>"
    if len(value) <= keep:
        return "*" * len(value)
    return "*" * (len(value) - keep) + value[-keep:]
