"""Execution helpers that keep live order mutation explicit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from schwab.utils import Utils


class LiveOrderConfirmationError(RuntimeError):
    """Raised when live order mutation lacks explicit confirmation."""


def load_order_file(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def require_live_confirmation(confirm_live_order: bool) -> None:
    if not confirm_live_order:
        raise LiveOrderConfirmationError(
            "Live Schwab order mutation requires --confirm-live-order"
        )


def preview_order(client: Any, account_hash: str, order_spec: dict[str, Any]) -> Any:
    response = client.preview_order(account_hash, order_spec)
    response.raise_for_status()
    return response.json() if response.content else None


def place_order(
    client: Any,
    account_hash: str,
    order_spec: dict[str, Any],
    *,
    confirm_live_order: bool = False,
) -> str | None:
    require_live_confirmation(confirm_live_order)
    response = client.place_order(account_hash, order_spec)
    response.raise_for_status()
    return Utils(client, account_hash).extract_order_id(response)


def cancel_order(
    client: Any,
    account_hash: str,
    order_id: str,
    *,
    confirm_live_order: bool = False,
) -> None:
    require_live_confirmation(confirm_live_order)
    response = client.cancel_order(order_id, account_hash)
    response.raise_for_status()


def replace_order(
    client: Any,
    account_hash: str,
    order_id: str,
    order_spec: dict[str, Any],
    *,
    confirm_live_order: bool = False,
) -> None:
    require_live_confirmation(confirm_live_order)
    response = client.replace_order(account_hash, order_id, order_spec)
    response.raise_for_status()
