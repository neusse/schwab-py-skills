from __future__ import annotations

from schwab_py_skills.orders.executor import cancel_order, preview_order, replace_order


class FakeResponse:
    content = b"{}"

    def __init__(self) -> None:
        self.raised = False

    def raise_for_status(self) -> None:
        self.raised = True

    def json(self):
        return {"ok": True}


class FakeClient:
    def __init__(self) -> None:
        self.calls = []

    def preview_order(self, account_hash, order_spec):
        self.calls.append(("preview", account_hash, order_spec))
        return FakeResponse()

    def cancel_order(self, order_id, account_hash):
        self.calls.append(("cancel", order_id, account_hash))
        return FakeResponse()

    def replace_order(self, account_hash, order_id, order_spec):
        self.calls.append(("replace", account_hash, order_id, order_spec))
        return FakeResponse()


def test_preview_order_does_not_require_live_confirmation() -> None:
    client = FakeClient()

    assert preview_order(client, "hash", {"order": True}) == {"ok": True}
    assert client.calls == [("preview", "hash", {"order": True})]


def test_cancel_and_replace_require_but_accept_confirmation() -> None:
    client = FakeClient()

    cancel_order(client, "hash", "123", confirm_live_order=True)
    replace_order(client, "hash", "123", {"order": True}, confirm_live_order=True)

    assert client.calls[0] == ("cancel", "123", "hash")
    assert client.calls[1] == ("replace", "hash", "123", {"order": True})
