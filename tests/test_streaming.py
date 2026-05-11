from __future__ import annotations

import asyncio

from schwab_py_skills import streaming


class FakeStreamClient:
    def __init__(self, client):
        self.client = client
        self.handler = None
        self.logged_out = False
        self.subscribed = None
        self.count = 0

    def add_level_one_equity_handler(self, handler):
        self.handler = handler

    async def login(self):
        return None

    async def level_one_equity_subs(self, symbols, fields=None):
        self.subscribed = (symbols, fields)

    async def handle_message(self):
        self.count += 1
        self.handler({"symbol": "AAPL"})
        if self.count > 1:
            await asyncio.sleep(1)

    async def logout(self):
        self.logged_out = True


def test_stream_level_one_equities_uses_handler_and_logs_out(monkeypatch) -> None:
    created = {}

    def factory(client):
        instance = FakeStreamClient(client)
        created["instance"] = instance
        return instance

    messages = []
    monkeypatch.setattr(streaming, "StreamClient", factory)

    asyncio.run(
        streaming.stream_level_one_equities(
            object(),
            ["AAPL"],
            duration=0,
            handler=messages.append,
        )
    )

    instance = created["instance"]
    assert instance.subscribed == (["AAPL"], None)
    assert instance.logged_out


def test_stream_service_supports_account_activity(monkeypatch) -> None:
    calls = []

    class AccountActivityStream(FakeStreamClient):
        def add_account_activity_handler(self, handler):
            calls.append("handler")
            self.handler = handler

        async def account_activity_sub(self):
            calls.append("sub")

    def factory(client):
        instance = AccountActivityStream(client)
        created["instance"] = instance
        return instance

    created = {}
    monkeypatch.setattr(streaming, "StreamClient", factory)

    asyncio.run(streaming.stream_service(object(), "account-activity", duration=0))

    assert calls == ["handler", "sub"]
    assert created["instance"].logged_out
