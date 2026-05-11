# Schwab-Py Codex Skills

Codex-first skills and local Python utilities for working with Schwab through
[`schwab-py`](https://schwab-py.readthedocs.io/en/latest/). This repo is designed
to avoid Schwab MCP usage for normal workflows and keep token use low by giving
Codex direct, repeatable commands.

## Install

```powershell
python -m pip install -e .[dev]
```

## Required Environment

Set these before using live Schwab calls:

- `SCHWAB_API_KEY`
- `SCHWAB_APP_SECRET`
- `SCHWAB_CALLBACK_URL`
- `SCHWAB_TOKEN_PATH`

`SCHWAB_TOKEN_PATH` is required and shared with other Schwab apps. This project
does not choose a default, move it, or recreate it somewhere else. Point it at
your existing Schwab token file.

Lowercase `schwab_*` names are accepted only as compatibility fallbacks for older
tools. The documented interface for this repo is uppercase `SCHWAB_*`.

Inspect or configure the environment:

```powershell
python -m schwab_py_skills.setup_env --show
python -m schwab_py_skills.setup_env
```

## Skills

Project skills live under `.codex/skills/`:

- `schwab-setup` - inspect and configure Schwab environment variables.
- `schwab-auth-client` - validate token/client/account-hash readiness.
- `schwab-market-data` - quotes, price history, option chains, instruments, fundamentals, movers, and hours.
- `schwab-portfolio` - account hashes, balances, positions, transactions, and order history.
- `schwab-orders` - dry-run-first order building, previewing, placing, canceling, replacing, and order ID extraction.
- `schwab-streaming` - streaming quote, chart, book, screener, and account activity workflows.

For Codex-level user instructions, examples, expected behavior, output shapes,
and safety rules, see [docs/CODEX_SKILL_USAGE.md](docs/CODEX_SKILL_USAGE.md).
For deeper order examples, see [docs/ORDER_STRATEGY_EXAMPLES.md](docs/ORDER_STRATEGY_EXAMPLES.md).
For local skill deployment, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Using These As Codex Skills

Open Codex in this repo and invoke the skill by name at the start of the prompt:

```text
/schwab-market-data get a quote for AAPL and MSFT
/schwab-market-data get a quote for AAPL and MSFT show last price and fundamentals in a table
/schwab-portfolio show me a table of all my positions of all accounts combined
/schwab-orders show me a bracket order JSON for AAPL 1 share with normal risk stops
/schwab-streaming AAPL MSFT
```

Codex should load the matching `.codex/skills/<skill-name>/SKILL.md`, run the
repo-local script, then format the result for the user. When the user asks for
full JSON, Codex should return the raw command output. When the user asks for a
table or comparison, Codex should extract the relevant fields and keep enough
source detail to answer follow-ups.

## Order Safety

Order commands build and print JSON by default. Live mutation requires explicit
flags:

```powershell
python scripts\place_order.py --order-file order.json --account-hash HASH --confirm-live-order
```

Previewing uses Schwab's `preview_order` endpoint and is allowed without placing
an order:

```powershell
python scripts\preview_order.py --order-file order.json --account-hash HASH
```

## Examples

```powershell
python scripts\check_auth.py
python scripts\token_info.py
python scripts\get_quotes.py AAPL MSFT
python scripts\get_quotes.py AAPL --fields quote fundamental
python scripts\get_price_history.py AAPL --period-type day --period one-day --frequency-type minute --frequency every-minute
python scripts\get_option_chain.py AAPL --contract-type call --strike-count 10 --include-underlying-quote
python scripts\get_option_expirations.py AAPL
python scripts\get_instruments.py AAPL --projection fundamental
python scripts\get_market_hours.py --markets equity option
python scripts\get_movers.py --index spx --sort-order percent-change-up --frequency five
python scripts\get_portfolio.py --positions
python scripts\get_portfolio.py --all-linked --positions
python scripts\get_transactions.py --symbol AAPL --transaction-type trade
python scripts\get_orders.py --status filled --max-results 10
python scripts\build_equity_order.py --side buy --symbol AAPL --qty 1 --type limit --price 150
python scripts\build_option_order.py --action buy-to-open --symbol "AAPL  260117C00150000" --contracts 1 --limit 1.25
python scripts\build_spread_order.py --strategy vertical --long "AAPL  260117C00145000" --short "AAPL  260117C00150000" --contracts 1 --net-debit 2.00
python scripts\build_strategy_order.py bracket --symbol AAPL --qty 1 --entry-price 291.34 --profit-target 303.00 --stop-loss 285.52
python scripts\build_strategy_order.py iron-condor --put-long "AAPL  260117P00280000" --put-short "AAPL  260117P00285000" --call-short "AAPL  260117C00300000" --call-long "AAPL  260117C00305000" --contracts 1 --net-credit 1.25
python scripts\stream_quotes.py --symbols AAPL MSFT --duration 30 --fields bid-price ask-price last-price total-volume
python scripts\stream_quotes.py --service account-activity --duration 30
```

Live order maintenance commands:

```powershell
python scripts\get_order.py --order-id 123 --account-hash HASH
python scripts\cancel_order.py --order-id 123 --account-hash HASH --confirm-live-order
python scripts\replace_order.py --order-id 123 --order-file replacement.json --account-hash HASH --confirm-live-order
```

## Deploy Codex Skills Locally

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\deploy-skills.ps1 -WhatIf
pwsh -ExecutionPolicy Bypass -File .\scripts\deploy-skills.ps1
```

## Validation

```powershell
python -m compileall src scripts tests
python -m pytest
python -m ruff check .
```
