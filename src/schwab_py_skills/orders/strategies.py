"""Curated multi-leg strategy helpers."""

from __future__ import annotations

from .builder import OrderBuilder
from .schemas import AssetType, OrderAction


def vertical_spread(
    long_symbol: str,
    short_symbol: str,
    contracts: int,
    *,
    net_debit: float | None = None,
    net_credit: float | None = None,
) -> OrderBuilder:
    order = (
        OrderBuilder()
        .with_leg(OrderAction.BUY_TO_OPEN, long_symbol, contracts, AssetType.OPTION)
        .with_leg(OrderAction.SELL_TO_OPEN, short_symbol, contracts, AssetType.OPTION)
        .vertical_spread()
        .day()
    )
    if net_debit is not None:
        return order.net_debit(net_debit)
    if net_credit is not None:
        return order.net_credit(net_credit)
    return order.net_zero()


def iron_condor(
    put_long: str,
    put_short: str,
    call_short: str,
    call_long: str,
    contracts: int,
    *,
    net_credit: float,
) -> OrderBuilder:
    return (
        OrderBuilder()
        .with_leg(OrderAction.SELL_TO_OPEN, put_short, contracts, AssetType.OPTION)
        .with_leg(OrderAction.BUY_TO_OPEN, put_long, contracts, AssetType.OPTION)
        .with_leg(OrderAction.SELL_TO_OPEN, call_short, contracts, AssetType.OPTION)
        .with_leg(OrderAction.BUY_TO_OPEN, call_long, contracts, AssetType.OPTION)
        .iron_condor_strategy()
        .net_credit(net_credit)
        .day()
    )


def bracket_order(
    symbol: str,
    quantity: int,
    entry_price: float,
    profit_target: float,
    stop_loss: float,
) -> OrderBuilder:
    profit = OrderBuilder().sell(symbol).shares(quantity).limit(profit_target).gtc()
    stop = OrderBuilder().sell(symbol).shares(quantity).stop(stop_loss).gtc()
    exit_oco = profit.one_cancels_other(stop)
    return OrderBuilder().buy(symbol).shares(quantity).limit(entry_price).day().one_triggers_other(exit_oco)


def straddle(call_symbol: str, put_symbol: str, contracts: int, *, net_debit: float) -> OrderBuilder:
    return (
        OrderBuilder()
        .with_leg(OrderAction.BUY_TO_OPEN, call_symbol, contracts, AssetType.OPTION)
        .with_leg(OrderAction.BUY_TO_OPEN, put_symbol, contracts, AssetType.OPTION)
        .straddle_strategy()
        .net_debit(net_debit)
        .day()
    )


def strangle(call_symbol: str, put_symbol: str, contracts: int, *, net_debit: float) -> OrderBuilder:
    return (
        OrderBuilder()
        .with_leg(OrderAction.BUY_TO_OPEN, call_symbol, contracts, AssetType.OPTION)
        .with_leg(OrderAction.BUY_TO_OPEN, put_symbol, contracts, AssetType.OPTION)
        .strangle_strategy()
        .net_debit(net_debit)
        .day()
    )


def covered_call(
    underlying: str,
    shares: int,
    call_symbol: str,
    contracts: int,
    stock_limit: float | None = None,
    call_limit: float | None = None,
) -> list[OrderBuilder]:
    stock = OrderBuilder().buy(underlying).shares(shares)
    stock = stock.limit(stock_limit) if stock_limit is not None else stock.market()
    call = OrderBuilder().sell_to_open(call_symbol).contracts(contracts)
    call = call.limit(call_limit) if call_limit is not None else call.market()
    return [stock.day(), call.day()]
