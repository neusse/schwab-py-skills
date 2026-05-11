---
name: schwab-market-data
description: Use when fetching Schwab quotes, price history, option chains, instruments, fundamentals, movers, or market hours through schwab-py.
---

# Schwab Market Data

Use `schwab-py` client methods directly through repo scripts or short Python snippets.

## Quotes

```powershell
python scripts\get_quotes.py AAPL MSFT
python scripts\get_quotes.py AAPL --fields quote fundamental
python scripts\get_price_history.py AAPL --period-type day --period one-day --frequency-type minute --frequency every-minute
python scripts\get_option_chain.py AAPL --contract-type call --strike-count 10 --include-underlying-quote
python scripts\get_option_expirations.py AAPL
python scripts\get_instruments.py AAPL --projection fundamental
python scripts\get_market_hours.py --markets equity option
python scripts\get_movers.py --index spx --sort-order percent-change-up --frequency five
```

## Coverage

Use the Schwab client for:

- current quotes and multi-quotes
- price history
- option chains
- option expiration chains
- instrument search and fundamentals
- movers and market hours

## Rules

- Do not use Schwab MCP for these workflows.
- Keep raw JSON when the user needs complete fields.
- Summarize only after preserving enough payload detail for follow-up analysis.
