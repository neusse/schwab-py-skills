# Order Strategy Examples

These examples are dry-run builders. They print Schwab-compatible JSON and do
not submit orders. Live order mutation still requires `--confirm-live-order`
through `place_order.py`, `cancel_order.py`, or `replace_order.py`.

## Plain Equity Order

```powershell
python scripts\build_equity_order.py --side buy --symbol AAPL --qty 1 --type limit --price 291.34
```

Use for single-leg stock orders. The output can be reviewed directly or saved
to a file for Schwab preview:

```powershell
python scripts\build_equity_order.py --side buy --symbol AAPL --qty 1 --type limit --price 291.34 > order.json
python scripts\preview_order.py --order-file order.json --account-hash <hash>
```

## Bracket Order

```powershell
python scripts\build_strategy_order.py bracket --symbol AAPL --qty 1 --entry-price 291.34 --profit-target 303.00 --stop-loss 285.52
```

Shape:

- parent `BUY` limit order
- child `OCO`
- profit-target `SELL` limit
- stop-loss `SELL` stop

Codex prompt:

```text
/schwab-orders show me a bracket order JSON for AAPL 1 share with normal risk stops
```

For vague language like "normal risk", Codex should state the chosen assumption
before showing JSON. A simple default is a 2 percent stop and 4 percent target
from the current last price.

## Vertical Spread

```powershell
python scripts\build_strategy_order.py vertical --long "AAPL  260117C00145000" --short "AAPL  260117C00150000" --contracts 1 --net-debit 2.00
```

Use `--net-credit` instead of `--net-debit` for credit spreads.

## Iron Condor

```powershell
python scripts\build_strategy_order.py iron-condor --put-long "AAPL  260117P00280000" --put-short "AAPL  260117P00285000" --call-short "AAPL  260117C00300000" --call-long "AAPL  260117C00305000" --contracts 1 --net-credit 1.25
```

The leg order is:

- sell put
- buy put
- sell call
- buy call

## Straddle

```powershell
python scripts\build_strategy_order.py straddle --call "AAPL  260117C00290000" --put "AAPL  260117P00290000" --contracts 1 --net-debit 12.50
```

## Strangle

```powershell
python scripts\build_strategy_order.py strangle --call "AAPL  260117C00300000" --put "AAPL  260117P00280000" --contracts 1 --net-debit 8.25
```

## Covered Call

```powershell
python scripts\build_strategy_order.py covered-call --underlying AAPL --shares 100 --call "AAPL  260117C00300000" --contracts 1 --stock-limit 291.34 --call-limit 4.25
```

This returns a JSON list because it is represented as a stock order plus a short
call order. Preview each order separately before any live placement.

## Preview And Placement Flow

1. Build JSON.
2. Save it to a local file.
3. Preview with Schwab.
4. Only place after explicit confirmation.

```powershell
python scripts\build_strategy_order.py vertical --long "AAPL  260117C00145000" --short "AAPL  260117C00150000" --contracts 1 --net-debit 2.00 > order.json
python scripts\preview_order.py --order-file order.json --account-hash <hash>
python scripts\place_order.py --order-file order.json --account-hash <hash> --confirm-live-order
```

## Codex Output Rules

- If the user asks for JSON, show the built order JSON.
- If the user asks for preview, call Schwab's preview endpoint.
- If the user asks for live placement, require explicit confirmation and use
  `--confirm-live-order`.
- If the user provides vague strategy terms, state concrete assumptions before
  building the order.
