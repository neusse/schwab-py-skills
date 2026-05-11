from __future__ import annotations

import pytest

from schwab_py_skills.orders.builder import OrderBuilder
from schwab_py_skills.orders.executor import LiveOrderConfirmationError, require_live_confirmation
from schwab_py_skills.orders.strategies import bracket_order, vertical_spread
from schwab_py_skills.orders.templates import equity_order, option_order


def test_equity_limit_order_json() -> None:
    order = equity_order("buy", "AAPL", 1, "limit", 150.129).build()

    assert order["orderType"] == "LIMIT"
    assert order["price"] == "150.12"
    assert order["orderLegCollection"][0]["instruction"] == "BUY"


def test_option_order_json() -> None:
    order = option_order("buy-to-open", "AAPL  260117C00150000", 1, 1.25).build()

    assert order["orderLegCollection"][0]["instrument"]["assetType"] == "OPTION"
    assert order["orderLegCollection"][0]["instruction"] == "BUY_TO_OPEN"


def test_vertical_spread_json() -> None:
    order = vertical_spread("LONG", "SHORT", 1, net_debit=0.75).build()

    assert order["orderType"] == "NET_DEBIT"
    assert order["complexOrderStrategyType"] == "VERTICAL"
    assert len(order["orderLegCollection"]) == 2


def test_bracket_order_uses_trigger_and_oco() -> None:
    order = bracket_order("AAPL", 1, 150, 160, 140).build()

    assert order["orderStrategyType"] == "TRIGGER"
    child = order["childOrderStrategies"][0]
    assert child["orderStrategyType"] == "OCO"


def test_builder_requires_quantity() -> None:
    with pytest.raises(ValueError):
        OrderBuilder().buy("AAPL").limit(150).build()


def test_live_confirmation_required() -> None:
    with pytest.raises(LiveOrderConfirmationError):
        require_live_confirmation(False)
