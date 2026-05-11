"""Async streaming helpers for schwab-py StreamClient."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Awaitable
from typing import Any, Callable

from schwab.streaming import StreamClient
from websockets.exceptions import ConnectionClosedOK


def print_json_message(message: Any) -> None:
    print(json.dumps(message, indent=2, default=str), flush=True)


async def stream_level_one_equities(
    client: Any,
    symbols: list[str],
    *,
    duration: int = 30,
    fields: list[Any] | None = None,
    handler: Callable[[Any], None] = print_json_message,
) -> None:
    """Subscribe to level-one equity quote messages for a bounded duration."""

    stream_client = StreamClient(client)
    stream_client.add_level_one_equity_handler(handler)
    await stream_client.login()
    try:
        await stream_client.level_one_equity_subs(symbols, fields=fields)
        end_time = time.monotonic() + duration
        while True:
            remaining = end_time - time.monotonic()
            if remaining <= 0:
                break
            try:
                await asyncio.wait_for(stream_client.handle_message(), timeout=remaining)
            except asyncio.TimeoutError:
                break
    finally:
        await _safe_logout(stream_client)


async def stream_service(
    client: Any,
    service: str,
    *,
    symbols: list[str] | None = None,
    duration: int = 30,
    fields: list[Any] | None = None,
    handler: Callable[[Any], None] = print_json_message,
) -> None:
    """Subscribe to a supported Schwab stream service for a bounded duration."""

    stream_client = StreamClient(client)
    normalized = service.lower().replace("_", "-")
    service_methods: dict[str, tuple[str, str]] = {
        "level-one-equity": ("add_level_one_equity_handler", "level_one_equity_subs"),
        "level-one-option": ("add_level_one_option_handler", "level_one_option_subs"),
        "chart-equity": ("add_chart_equity_handler", "chart_equity_subs"),
        "nasdaq-book": ("add_nasdaq_book_handler", "nasdaq_book_subs"),
        "nyse-book": ("add_nyse_book_handler", "nyse_book_subs"),
        "options-book": ("add_options_book_handler", "options_book_subs"),
        "screener-equity": ("add_screener_equity_handler", "screener_equity_subs"),
        "screener-option": ("add_screener_option_handler", "screener_option_subs"),
        "account-activity": ("add_account_activity_handler", "account_activity_sub"),
    }
    if normalized not in service_methods:
        choices = ", ".join(sorted(service_methods))
        raise ValueError(f"Unsupported streaming service: {service}. Choices: {choices}")

    handler_method_name, subscription_method_name = service_methods[normalized]
    add_handler: Callable[[Callable[[Any], None]], None] = getattr(stream_client, handler_method_name)
    subscribe: Callable[..., Awaitable[Any]] = getattr(stream_client, subscription_method_name)
    add_handler(handler)
    await stream_client.login()
    try:
        if normalized == "account-activity":
            await subscribe()
        else:
            if not symbols:
                raise ValueError(f"{service} requires at least one symbol")
            if normalized.startswith("level-one"):
                await subscribe(symbols, fields=fields)
            else:
                await subscribe(symbols)

        end_time = time.monotonic() + duration
        while True:
            remaining = end_time - time.monotonic()
            if remaining <= 0:
                break
            try:
                await asyncio.wait_for(stream_client.handle_message(), timeout=remaining)
            except asyncio.TimeoutError:
                break
    finally:
        await _safe_logout(stream_client)


async def _safe_logout(stream_client: StreamClient) -> None:
    try:
        await stream_client.logout()
    except ConnectionClosedOK:
        return
