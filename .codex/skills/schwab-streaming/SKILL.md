---
name: schwab-streaming
description: Use when subscribing to Schwab streaming quotes, options quotes, charts, order books, screeners, or account activity through schwab-py StreamClient.
---

# Schwab Streaming

Use this skill for Schwab streaming workflows with `schwab-py` `StreamClient`.

## Smoke Command

```powershell
python scripts\stream_quotes.py --symbols AAPL MSFT --duration 30 --fields bid-price ask-price last-price total-volume
python scripts\stream_quotes.py --service level-one-option --symbols "AAPL  260117C00150000" --duration 30
python scripts\stream_quotes.py --service chart-equity --symbols AAPL --duration 30
python scripts\stream_quotes.py --service nasdaq-book --symbols AAPL --duration 30
python scripts\stream_quotes.py --service screener-equity --symbols "$SPX" --duration 30
python scripts\stream_quotes.py --service account-activity --duration 30
```

The script creates a `schwab-py` `StreamClient`, logs in, subscribes to
the requested service, prints JSON messages, and logs out after the duration.

## Coverage

- level-one equity quotes
- level-one option quotes
- OHLCV charts
- level-two order books
- screeners
- account activity

## Rules

- Use streaming only after `schwab-auth-client` passes.
- Keep handlers narrow and print compact JSON events.
- Prefer short duration smoke tests before long-running streams.
