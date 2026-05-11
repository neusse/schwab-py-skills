# Codex Skill Usage Guide

This repo is meant to be used from Codex through project-local skills in
`.codex/skills/`. The skills are thin operational wrappers around local Python
commands that call `schwab-py` directly. They are not MCP tools and should not
route normal Schwab work through a Schwab MCP server.

## How To Invoke Skills

In a Codex chat opened at this repo, call a skill by name at the start of the
request:

```text
/schwab-market-data get a quote for AAPL and MSFT
/schwab-portfolio show me all linked account positions combined
/schwab-orders show me a dry-run bracket order JSON for AAPL
/schwab-streaming stream AAPL and MSFT for 10 seconds
```

Codex should read the matching `.codex/skills/<skill-name>/SKILL.md`, run the
repo-local Python command, and summarize or format the returned data for the
user. If the user asks for raw output, Codex should return the full JSON returned
by the command.

## Skill Catalog

| Skill | Use it for | Typical Codex requests |
|---|---|---|
| `schwab-setup` | Environment variables and token path readiness. | `/schwab-setup show my Schwab env setup` |
| `schwab-auth-client` | Client creation, token file checks, account-hash readiness. | `/schwab-auth-client check whether auth works` |
| `schwab-market-data` | Quotes, fundamentals, price history, option chains, movers, market hours. | `/schwab-market-data compare AAPL and MSFT fundamentals` |
| `schwab-portfolio` | Linked accounts, balances, positions, transactions, order history. | `/schwab-portfolio show all positions combined` |
| `schwab-orders` | Dry-run order JSON, Schwab preview, place/cancel/replace with confirmation. | `/schwab-orders build a vertical spread JSON for AAPL` |
| `schwab-streaming` | Bounded streaming for quotes, options, charts, books, screeners, account activity. | `/schwab-streaming AAPL MSFT for 30 seconds` |

## Global Safety Rules

- Use `schwab-py` directly through this repo's scripts and package.
- Do not use Schwab MCP for these workflows.
- Never invent, move, or replace `SCHWAB_TOKEN_PATH`.
- Redact account numbers, account hashes, and token details in chat summaries
  unless the user explicitly asks for raw output.
- Preserve raw JSON when the user asks to inspect exact fields.
- Live order mutation requires explicit confirmation. Building JSON and Schwab
  preview are allowed without live placement.

## Setup Skill

Use `schwab-setup` when credentials, callback URL, token path, or Windows
environment persistence are the task.

Example requests:

```text
/schwab-setup show me whether the Schwab env vars are configured
/schwab-setup help me configure the missing Schwab env vars
```

Expected Codex behavior:

- Run `python -m schwab_py_skills.setup_env --show` for inspection.
- Run `python -m schwab_py_skills.setup_env` only when interactive setup is
  actually requested.
- Treat `SCHWAB_TOKEN_PATH` as required user-owned shared config.
- Do not create a default token file path.

## Auth Client Skill

Use `schwab-auth-client` when the question is whether Codex can create a client,
read the configured token, or resolve account hashes.

Example requests:

```text
/schwab-auth-client check auth
/schwab-auth-client show token status
/schwab-auth-client verify account-hash readiness
```

Expected Codex behavior:

- Run `python scripts\check_auth.py` for live account-number readiness.
- Run `python scripts\token_info.py` for token file status.
- If setup fails, route back to `schwab-setup`.
- Summarize token status without exposing access or refresh tokens.

## Market Data Skill

Use `schwab-market-data` for read-only market data.

Example requests:

```text
/schwab-market-data get a quote for AAPL and MSFT
/schwab-market-data get a quote for AAPL and MSFT show last price and fundamentals in a table
/schwab-market-data show the AAPL option chain near the money
/schwab-market-data get SPX movers sorted by percent change up
```

Expected Codex behavior:

- Use quote commands for current quote and fundamentals.
- Use option-chain commands for options data.
- Use price-history commands for candles and historical data.
- Format tables when the user asks for comparison.
- Return full JSON when the user asks for full output.
- If Schwab returns `invalidSymbols`, report the invalid symbols directly.

Common commands:

```powershell
python scripts\get_quotes.py AAPL MSFT --fields quote fundamental
python scripts\get_price_history.py AAPL --period-type day --period one-day --frequency-type minute --frequency every-minute
python scripts\get_option_chain.py AAPL --contract-type call --strike-count 10 --include-underlying-quote
python scripts\get_instruments.py AAPL --projection fundamental
python scripts\get_market_hours.py --markets equity option
python scripts\get_movers.py --index spx --sort-order percent-change-up --frequency five
```

## Portfolio Skill

Use `schwab-portfolio` for account and position inspection.

Example requests:

```text
/schwab-portfolio show me a table of all my positions of all accounts combined
/schwab-portfolio show recent AAPL transactions
/schwab-portfolio show filled orders from the last week
```

Expected Codex behavior:

- Use `--all-linked --positions` for combined portfolio views.
- Aggregate by symbol when the user asks for all accounts combined.
- Omit account identifiers from chat output unless explicitly requested.
- Do not place, cancel, or replace orders from this skill.

Common commands:

```powershell
python scripts\get_portfolio.py --all-linked --positions
python scripts\get_transactions.py --symbol AAPL --transaction-type trade
python scripts\get_orders.py --status filled --max-results 10
python scripts\get_order.py --order-id <order-id> --account-hash <hash>
```

## Orders Skill

Use `schwab-orders` for order JSON construction, Schwab preview, and explicitly
confirmed live order operations.

Example requests:

```text
/schwab-orders show me a bracket order JSON for AAPL 1 share with normal risk stops
/schwab-orders build a dry-run AAPL buy limit order for 1 share at 150
/schwab-orders preview this order JSON with Schwab
/schwab-orders cancel order 123 after I confirm live cancellation
```

Expected Codex behavior:

- Build JSON by default. Do not place the order.
- Use current quotes only when the user asks for price-derived stops or targets.
- For vague risk terms like "normal risk", state the chosen assumptions, such as
  a 2 percent stop and 4 percent target.
- Use `preview_order.py` before live placement when practical.
- Refuse live mutation unless the user explicitly requests it and the command
  includes `--confirm-live-order`.

Common commands:

```powershell
python scripts\build_equity_order.py --side buy --symbol AAPL --qty 1 --type limit --price 150
python scripts\build_option_order.py --action buy-to-open --symbol "AAPL  260117C00150000" --contracts 1 --limit 1.25
python scripts\build_spread_order.py --strategy vertical --long "AAPL  260117C00145000" --short "AAPL  260117C00150000" --contracts 1 --net-debit 2.00
python scripts\build_strategy_order.py bracket --symbol AAPL --qty 1 --entry-price 291.34 --profit-target 303.00 --stop-loss 285.52
python scripts\build_strategy_order.py covered-call --underlying AAPL --shares 100 --call "AAPL  260117C00300000" --contracts 1 --stock-limit 291.34 --call-limit 4.25
python scripts\preview_order.py --order-file order.json --account-hash <hash>
python scripts\place_order.py --order-file order.json --account-hash <hash> --confirm-live-order
python scripts\cancel_order.py --order-id <order-id> --account-hash <hash> --confirm-live-order
python scripts\replace_order.py --order-id <order-id> --order-file replacement.json --account-hash <hash> --confirm-live-order
```

See `docs/ORDER_STRATEGY_EXAMPLES.md` for bracket, vertical, iron condor,
straddle, strangle, and covered-call examples.

## Streaming Skill

Use `schwab-streaming` for short bounded streaming sessions.

Example requests:

```text
/schwab-streaming AAPL MSFT
/schwab-streaming stream AAPL and MSFT for 10 seconds with bid ask last
/schwab-streaming show account activity for 30 seconds
```

Expected Codex behavior:

- Default to `level-one-equity` for ticker symbols.
- Use short durations unless the user asks for a longer stream.
- Print compact event summaries unless the user asks for full stream JSON.
- Stop the stream at the requested duration and do not leave long-running
  terminal sessions active.

Common commands:

```powershell
python scripts\stream_quotes.py --symbols AAPL MSFT --duration 30 --fields bid-price ask-price last-price total-volume
python scripts\stream_quotes.py --service account-activity --duration 30
python scripts\stream_quotes.py --service chart-equity --symbols AAPL --duration 30
```

## Output Patterns

Codex should choose the output shape from the user request:

- "show full JSON" means return the complete command JSON.
- "table" means extract and compare the requested fields.
- "summary" means include only the fields needed to answer the question.
- "all accounts combined" means aggregate and hide account identifiers.
- "dry-run", "build", or "show JSON" for orders means do not submit.

## Troubleshooting

- Missing environment variables: use `/schwab-setup`.
- Token or account-hash failure: use `/schwab-auth-client`.
- Invalid ticker: report Schwab's `invalidSymbols` field.
- Streaming disconnect on timeout: normal close is acceptable; report received
  events and duration.
- Order preview rejection: show Schwab's reject/warn messages and do not place.
