"""Token inspection helpers."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

REFRESH_TOKEN_LIFETIME_DAYS = 7


def load_token_file(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _datetime_from_epoch(value: Any) -> str | None:
    if not isinstance(value, int | float):
        return None
    return datetime.fromtimestamp(value, tz=UTC).isoformat(timespec="seconds")


def token_summary(
    path: str | Path,
    token_age: float | None = None,
    now: float | None = None,
) -> dict[str, Any]:
    token_path = Path(path)
    payload = load_token_file(token_path) if token_path.exists() else {}
    token = payload.get("token", payload)
    created_at = payload.get("creation_timestamp")
    access_expires_at = token.get("expires_at")
    current_time = time.time() if now is None else now
    refresh_expires_at = None
    refresh_expires_in = None
    if isinstance(created_at, int | float):
        refresh_expires_at = created_at + timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS).total_seconds()
        refresh_expires_in = int(refresh_expires_at - current_time)

    return {
        "token_path": str(token_path),
        "token_exists": token_path.exists(),
        "access_token_present": bool(token.get("access_token")),
        "refresh_token_present": bool(token.get("refresh_token")),
        "created_at": created_at,
        "created_at_datetime": _datetime_from_epoch(created_at),
        "access_expires_at": access_expires_at,
        "access_expires_at_datetime": _datetime_from_epoch(access_expires_at),
        "access_expires_in": token.get("expires_in"),
        "refresh_expires_at_estimated": refresh_expires_at,
        "refresh_expires_at_estimated_datetime": _datetime_from_epoch(refresh_expires_at),
        "refresh_expires_in_estimated": refresh_expires_in,
        "expires_in": token.get("expires_in"),
        "scope": token.get("scope"),
        "token_age": token_age,
    }
