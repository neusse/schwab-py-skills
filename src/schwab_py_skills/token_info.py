"""Token inspection helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_token_file(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def token_summary(path: str | Path, token_age: float | None = None) -> dict[str, Any]:
    token_path = Path(path)
    payload = load_token_file(token_path) if token_path.exists() else {}
    token = payload.get("token", payload)
    return {
        "token_path": str(token_path),
        "token_exists": token_path.exists(),
        "access_token_present": bool(token.get("access_token")),
        "refresh_token_present": bool(token.get("refresh_token")),
        "expires_at": token.get("expires_at"),
        "expires_in": token.get("expires_in"),
        "scope": token.get("scope"),
        "token_age": token_age,
    }
