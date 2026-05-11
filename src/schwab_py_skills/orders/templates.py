"""Convenience wrappers for common order templates."""

from __future__ import annotations

from .builder import OrderBuilder


def equity_order(side: str, symbol: str, quantity: int, order_type: str, price: float | None = None):
    side = side.lower().replace("-", "_")
    builder = {
        "buy": OrderBuilder().buy,
        "sell": OrderBuilder().sell,
        "sell_short": OrderBuilder().sell_short,
        "buy_to_cover": OrderBuilder().buy_to_cover,
    }[side](symbol).shares(quantity)
    if order_type == "market":
        return builder.market()
    if order_type == "limit":
        if price is None:
            raise ValueError("Limit orders require --price")
        return builder.limit(price)
    raise ValueError(f"Unsupported equity order type: {order_type}")


def option_order(action: str, symbol: str, contracts: int, limit: float | None = None):
    action = action.lower().replace("-", "_")
    builder = {
        "buy_to_open": OrderBuilder().buy_to_open,
        "sell_to_close": OrderBuilder().sell_to_close,
        "sell_to_open": OrderBuilder().sell_to_open,
        "buy_to_close": OrderBuilder().buy_to_close,
    }[action](symbol).contracts(contracts)
    return builder.limit(limit) if limit is not None else builder.market()
