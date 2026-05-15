from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from collections import defaultdict
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from schwab_py_skills.client import create_client, response_json  # noqa: E402
from schwab_py_skills.market import get_option_chain, get_price_history, get_quotes  # noqa: E402
from schwab_py_skills.orders.strategies import bracket_order  # noqa: E402

DEMO_ROOT = Path(__file__).resolve().parent
PACIFIC = ZoneInfo("America/Los_Angeles")


def utc_iso(milliseconds: int | float | None) -> str | None:
    if milliseconds is None:
        return None
    return datetime.fromtimestamp(milliseconds / 1000, tz=UTC).isoformat(timespec="seconds")


def round_number(value: object, digits: int = 2) -> object:
    if isinstance(value, float):
        return round(value, digits)
    return value


def regular_session_rows(candles: list[dict[str, object]]) -> list[tuple[datetime, dict[str, object]]]:
    rows = []
    for candle in candles:
        timestamp = candle.get("datetime")
        if not isinstance(timestamp, int | float):
            continue
        local_time = datetime.fromtimestamp(timestamp / 1000, tz=UTC).astimezone(PACIFIC)
        if (local_time.hour, local_time.minute) >= (6, 30) and (
            local_time.hour,
            local_time.minute,
        ) <= (13, 0):
            rows.append((local_time, candle))
    return rows


def summarize_history(candles: list[dict[str, object]]) -> dict[str, object]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    chart = []
    for local_time, candle in regular_session_rows(candles):
        grouped[local_time.date().isoformat()].append(candle)
        close = candle.get("close")
        volume = candle.get("volume")
        if isinstance(close, int | float):
            chart.append(
                {
                    "time": local_time.strftime("%m-%d %H:%M"),
                    "close": round(float(close), 2),
                    "volume": int(volume) if isinstance(volume, int | float) else 0,
                }
            )

    days = []
    for day, day_candles in sorted(grouped.items()):
        days.append(
            {
                "date": day,
                "open": round_number(day_candles[0].get("open")),
                "high": round(max(float(c.get("high", 0)) for c in day_candles), 2),
                "low": round(min(float(c.get("low", 0)) for c in day_candles), 2),
                "close": round_number(day_candles[-1].get("close")),
                "volume": int(sum(float(c.get("volume", 0)) for c in day_candles)),
            }
        )

    period_change = None
    period_change_pct = None
    range_high = None
    range_low = None
    if days:
        first_open = float(days[0]["open"])
        last_close = float(days[-1]["close"])
        period_change = round(last_close - first_open, 2)
        period_change_pct = round((period_change / first_open) * 100, 2)
        range_high = round(max(float(day["high"]) for day in days), 2)
        range_low = round(min(float(day["low"]) for day in days), 2)

    return {
        "days": days,
        "chart": chart[-72:],
        "range_high": range_high,
        "range_low": range_low,
        "period_change": period_change,
        "period_change_pct": period_change_pct,
    }


def expiration_sort_key(key: str) -> tuple[int, str]:
    date, _, days = key.partition(":")
    return (int(days) if days.isdigit() else 999999, date)


def first_contract(side_map: dict[str, object], expiration: str, strike: float) -> dict[str, object]:
    expiration_map = side_map.get(expiration) or {}
    if not isinstance(expiration_map, dict):
        return {}
    contracts = expiration_map.get(f"{strike:.1f}") or expiration_map.get(str(strike)) or []
    return contracts[0] if contracts else {}


def option_rows(chain: dict[str, object], underlying: float) -> dict[str, object]:
    call_map = chain.get("callExpDateMap") or {}
    put_map = chain.get("putExpDateMap") or {}
    if not isinstance(call_map, dict) or not isinstance(put_map, dict):
        return {"expiration": None, "rows": [], "itm_calls": [], "itm_puts": []}

    expirations = sorted(set(call_map) | set(put_map), key=expiration_sort_key)
    if not expirations:
        return {"expiration": None, "rows": [], "itm_calls": [], "itm_puts": []}
    expiration = expirations[0]

    strike_set = set()
    for side_map in (call_map, put_map):
        expiration_map = side_map.get(expiration) or {}
        if isinstance(expiration_map, dict):
            strike_set.update(float(strike) for strike in expiration_map)
    near_strikes = sorted(strike_set, key=lambda strike: abs(strike - underlying))[:7]
    near_strikes = sorted(near_strikes)

    def row_for(contract: dict[str, object]) -> dict[str, object]:
        return {
            "bid": round_number(contract.get("bid")),
            "ask": round_number(contract.get("ask")),
            "last": round_number(contract.get("last")),
            "mark": round_number(contract.get("mark")),
            "delta": round_number(contract.get("delta"), 3),
            "gamma": round_number(contract.get("gamma"), 3),
            "theta": round_number(contract.get("theta"), 3),
            "vega": round_number(contract.get("vega"), 3),
            "volume": contract.get("totalVolume"),
            "open_interest": contract.get("openInterest"),
            "intrinsic": round_number(contract.get("intrinsicValue")),
            "extrinsic": round_number(contract.get("extrinsicValue")),
        }

    rows = []
    for strike in near_strikes:
        rows.append(
            {
                "strike": strike,
                "call": row_for(first_contract(call_map, expiration, strike)),
                "put": row_for(first_contract(put_map, expiration, strike)),
            }
        )

    def itm_rows(side_map: dict[str, object], side: str) -> list[dict[str, object]]:
        expiration_map = side_map.get(expiration) or {}
        if not isinstance(expiration_map, dict):
            return []
        selected = []
        for strike_key, contracts in expiration_map.items():
            if not contracts:
                continue
            strike = float(strike_key)
            contract = contracts[0]
            itm = contract.get("inTheMoney")
            if itm is None:
                itm = strike < underlying if side == "CALL" else strike > underlying
            if itm:
                selected.append({"strike": strike, **row_for(contract)})
        return sorted(selected, key=lambda row: abs(float(row["strike"]) - underlying))[:8]

    return {
        "expiration": expiration,
        "rows": rows,
        "itm_calls": itm_rows(call_map, "CALL"),
        "itm_puts": itm_rows(put_map, "PUT"),
    }


def build_decision(
    symbol: str,
    quote: dict[str, object],
    history: dict[str, object],
    options: dict[str, object],
) -> dict[str, object]:
    last_price = float(quote["last"])
    day_high = float(quote["high"])
    day_low = float(quote["low"])
    change_pct = float(quote["net_pct"])
    range_high = float(history["range_high"] or day_high)
    range_low = float(history["range_low"] or day_low)
    near_strikes = options["rows"]
    pivot = min((float(row["strike"]) for row in near_strikes), key=lambda strike: abs(strike - last_price))

    if change_pct >= 1 and last_price >= range_high:
        title = "Breakout pressure, require confirmation"
        stance = "Bullish watch"
        risk = "Medium"
        trigger = f"hold above {day_high:.2f}"
        body = (
            f"{symbol} is green and pressing the recent range high. Codex would wait for a hold "
            "above the high instead of chasing the first print."
        )
    elif change_pct <= -1 and last_price <= pivot:
        title = "Bearish pressure near the option pivot"
        stance = "Defensive watch"
        risk = "High"
        trigger = f"reclaim {pivot:.2f} or break below {day_low:.2f}"
        body = (
            f"{symbol} is red on the day and trading near the active option pivot. A reclaim "
            "can reset the setup; failure below the low keeps downside pressure active."
        )
    else:
        title = "Range decision, wait for clean direction"
        stance = "Neutral watch"
        risk = "Medium"
        trigger = f"break {day_high:.2f} or lose {day_low:.2f}"
        body = (
            f"{symbol} is inside the active decision range. Codex would favor alerts over "
            "a live order until price leaves the range."
        )

    stop = round(last_price * 0.98, 2)
    target = round(last_price * 1.04, 2)
    order_json = bracket_order(symbol, 1, last_price, target, stop).build()

    return {
        "title": title,
        "body": body,
        "stance": stance,
        "risk": risk,
        "confidence": "read-only",
        "trigger": trigger,
        "levels": {
            "support": [round(day_low, 2), round(range_low, 2)],
            "pivot": round(pivot, 2),
            "resistance": [round(day_high, 2), round(range_high, 2)],
        },
        "alerts": [
            {
                "level": "high" if risk == "High" else "medium",
                "title": "Live price at decision area",
                "meta": trigger,
                "confidence": "market-data",
            },
            {
                "level": "medium",
                "title": "0DTE option gamma is concentrated near spot",
                "meta": "Near-money deltas can reprice quickly if price moves through the pivot.",
                "confidence": "options",
            },
            {
                "level": "watch",
                "title": "Dry-run only",
                "meta": "This demo builds local JSON examples but exposes no trading endpoint.",
                "confidence": "safety",
            },
        ],
        "reasoning": [
            "Fetched live quote, 5-day price history, and option chain through schwab-py-skills.",
            "Compressed 30-minute history into daily context and a browser chart series.",
            "Selected the nearest expiration and strikes around live underlying price.",
            "Compared current price to daily range, 5-day range, and near-money option pivot.",
            "Generated a dry-run bracket example locally. No Schwab trading API is exposed.",
        ],
        "plan": {
            "title": "Dry-run bracket example, no live mutation",
            "text": "Generated from the latest quote with a 2 percent stop and 4 percent target. It is not submitted and this live demo has no route that can submit it.",
            "json": order_json,
        },
    }


def fetch_context(symbol: str) -> dict[str, object]:
    symbol = symbol.upper().strip()
    if not symbol.isalnum() or len(symbol) > 8:
        raise ValueError("Symbol must be 1-8 letters or numbers.")

    client = create_client()
    quote_payload = response_json(get_quotes(client, [symbol]))[symbol]
    quote = quote_payload["quote"]
    history_payload = response_json(
        get_price_history(
            client,
            symbol,
            period_type="day",
            period="five-days",
            frequency_type="minute",
            frequency="every-thirty-minutes",
        )
    )
    chain_payload = response_json(
        get_option_chain(client, symbol, contract_type="all", strike_count=12, include_underlying_quote=True)
    )

    last_price = float(quote.get("lastPrice") or quote.get("mark"))
    history = summarize_history(history_payload.get("candles", []))
    options = option_rows(chain_payload, float(chain_payload.get("underlyingPrice") or last_price))
    compact_quote = {
        "symbol": symbol,
        "description": quote_payload.get("reference", {}).get("description"),
        "last": round(last_price, 2),
        "bid": round_number(quote.get("bidPrice")),
        "ask": round_number(quote.get("askPrice")),
        "mark": round_number(quote.get("mark")),
        "net": round_number(quote.get("netChange")),
        "net_pct": round_number(quote.get("netPercentChange")),
        "open": round_number(quote.get("openPrice")),
        "high": round_number(quote.get("highPrice")),
        "low": round_number(quote.get("lowPrice")),
        "volume": quote.get("totalVolume"),
        "quote_utc": utc_iso(quote.get("quoteTime")),
        "fifty_two_week_high": round_number(quote.get("52WeekHigh")),
        "fifty_two_week_low": round_number(quote.get("52WeekLow")),
    }
    return {
        "symbol": symbol,
        "quote": compact_quote,
        "history": history,
        "options": options,
        "decision": build_decision(symbol, compact_quote, history, options),
        "safety": {
            "read_only": True,
            "trading_routes": False,
            "message": "Live demo uses Schwab market-data calls only. It does not expose order placement, preview, cancel, or replace routes.",
        },
    }


class LiveDemoHandler(BaseHTTPRequestHandler):
    server_version = "SchwabCodexLiveDemo/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/context":
            query = parse_qs(parsed.query)
            symbol = query.get("symbol", ["AAPL"])[0]
            try:
                self.write_json(fetch_context(symbol))
            except Exception as exc:  # noqa: BLE001
                self.write_json({"error": str(exc)}, status=500)
            return

        path = parsed.path if parsed.path != "/" else "/index.html"
        target = (DEMO_ROOT / path.lstrip("/")).resolve()
        if not str(target).startswith(str(DEMO_ROOT.resolve())) or not target.is_file():
            self.send_error(404)
            return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def write_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        timestamp = datetime.now(tz=UTC).isoformat(timespec="seconds")
        print(f"{timestamp} {self.address_string()} {format % args}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the read-only Schwab Codex live demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8778)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), LiveDemoHandler)
    print(f"Schwab Codex live demo running at http://{args.host}:{args.port}", flush=True)
    print("Read-only: no trading routes are exposed.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
