"""Market data wrappers over schwab-py client methods."""

from __future__ import annotations

from typing import Any

from schwab.client import Client

from .datetime_utils import parse_date, parse_datetime
from .enums import clean_none, enum_list, enum_value


def get_quotes(client: Any, symbols: list[str], fields: list[str] | None = None) -> Any:
    kwargs = clean_none({"fields": enum_list(Client.Quote.Fields, fields)})
    return client.get_quotes(symbols, **kwargs)


def get_price_history(
    client: Any,
    symbol: str,
    *,
    period_type: str | None = None,
    period: str | None = None,
    frequency_type: str | None = None,
    frequency: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    extended_hours: bool | None = None,
    previous_close: bool | None = None,
) -> Any:
    kwargs = clean_none(
        {
            "period_type": enum_value(Client.PriceHistory.PeriodType, period_type),
            "period": enum_value(Client.PriceHistory.Period, period),
            "frequency_type": enum_value(Client.PriceHistory.FrequencyType, frequency_type),
            "frequency": enum_value(Client.PriceHistory.Frequency, frequency),
            "start_datetime": parse_datetime(start_datetime),
            "end_datetime": parse_datetime(end_datetime),
            "need_extended_hours_data": extended_hours,
            "need_previous_close": previous_close,
        }
    )
    return client.get_price_history(symbol, **kwargs)


def get_option_chain(
    client: Any,
    symbol: str,
    *,
    contract_type: str | None = None,
    strike_count: int | None = None,
    strategy: str | None = None,
    strike: float | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    include_underlying_quote: bool | None = None,
) -> Any:
    kwargs = clean_none(
        {
            "contract_type": enum_value(Client.Options.ContractType, contract_type),
            "strike_count": strike_count,
            "strategy": enum_value(Client.Options.Strategy, strategy),
            "strike": strike,
            "from_date": parse_date(from_date),
            "to_date": parse_date(to_date),
            "include_underlying_quote": include_underlying_quote,
        }
    )
    return client.get_option_chain(symbol, **kwargs)


def get_instruments(client: Any, symbols: list[str], projection: str) -> Any:
    return client.get_instruments(symbols, enum_value(Client.Instrument.Projection, projection))


def get_market_hours(client: Any, markets: list[str], date_value: str | None = None) -> Any:
    market_values = enum_list(Client.MarketHours.Market, markets)
    return client.get_market_hours(market_values, date=parse_date(date_value))


def get_movers(
    client: Any,
    index: str,
    *,
    sort_order: str | None = None,
    frequency: str | None = None,
) -> Any:
    kwargs = clean_none(
        {
            "sort_order": enum_value(Client.Movers.SortOrder, sort_order),
            "frequency": enum_value(Client.Movers.Frequency, frequency),
        }
    )
    return client.get_movers(enum_value(Client.Movers.Index, index), **kwargs)
