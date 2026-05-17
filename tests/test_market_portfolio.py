from __future__ import annotations

from schwab.client import Client

from schwab_py_skills.market import get_movers, get_option_chain, get_option_expirations, get_price_history
from schwab_py_skills.portfolio import get_orders_for_account, get_transactions


class FakeClient:
    def __init__(self) -> None:
        self.calls = []

    def get_price_history(self, symbol, **kwargs):
        self.calls.append(("price_history", symbol, kwargs))
        return "ok"

    def get_option_chain(self, symbol, **kwargs):
        self.calls.append(("option_chain", symbol, kwargs))
        return "ok"

    def get_option_expiration_chain(self, symbol):
        self.calls.append(("option_expirations", symbol))
        return "ok"

    def get_movers(self, index, **kwargs):
        self.calls.append(("movers", index, kwargs))
        return "ok"

    def get_transactions(self, account_hash, **kwargs):
        self.calls.append(("transactions", account_hash, kwargs))
        return "ok"

    def get_orders_for_account(self, account_hash, **kwargs):
        self.calls.append(("orders", account_hash, kwargs))
        return "ok"


def test_market_wrappers_convert_enums() -> None:
    client = FakeClient()

    get_price_history(client, "AAPL", period_type="day", frequency="every-minute")
    get_option_chain(client, "AAPL", contract_type="call", strategy="single")
    get_option_expirations(client, "AAPL")
    get_movers(client, "spx", sort_order="percent-change-up", frequency="five")

    assert client.calls[0][2]["period_type"] == Client.PriceHistory.PeriodType.DAY
    assert client.calls[0][2]["frequency"] == Client.PriceHistory.Frequency.EVERY_MINUTE
    assert client.calls[1][2]["contract_type"] == Client.Options.ContractType.CALL
    assert client.calls[2] == ("option_expirations", "AAPL")
    assert client.calls[3][1] == Client.Movers.Index.SPX


def test_portfolio_wrappers_convert_dates_and_enums() -> None:
    client = FakeClient()

    get_transactions(client, "hash", transaction_type="trade", symbol="AAPL")
    get_orders_for_account(client, "hash", status="filled", max_results=10)

    assert client.calls[0][2]["transaction_types"] == Client.Transactions.TransactionType.TRADE
    assert client.calls[1][2]["status"] == Client.Order.Status.FILLED
    assert client.calls[1][2]["max_results"] == 10
