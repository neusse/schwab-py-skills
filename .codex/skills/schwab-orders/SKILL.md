---
name: schwab-orders
description: Use when building, previewing, placing, canceling, replacing, or extracting IDs for Schwab equity, option, spread, bracket, OCO, or trigger orders through schwab-py.
---

# Schwab Orders

Order workflows are dry-run-first. Live place, cancel, and replace require explicit confirmation flags.

## Build

```powershell
python scripts\build_equity_order.py --side buy --symbol AAPL --qty 1 --type limit --price 150
python scripts\build_option_order.py --action buy-to-open --symbol "AAPL  260117C00150000" --contracts 1 --limit 1.25
python scripts\build_spread_order.py --strategy vertical --long "AAPL  260117C00145000" --short "AAPL  260117C00150000" --contracts 1 --net-debit 2.00
python scripts\build_strategy_order.py bracket --symbol AAPL --qty 1 --entry-price 291.34 --profit-target 303.00 --stop-loss 285.52
python scripts\build_strategy_order.py iron-condor --put-long "AAPL  260117P00280000" --put-short "AAPL  260117P00285000" --call-short "AAPL  260117C00300000" --call-long "AAPL  260117C00305000" --contracts 1 --net-credit 1.25
```

## Preview

```powershell
python scripts\preview_order.py --order-file order.json --account-hash <hash>
```

## Place

```powershell
python scripts\place_order.py --order-file order.json --account-hash <hash> --confirm-live-order
python scripts\cancel_order.py --order-id <order-id> --account-hash <hash> --confirm-live-order
python scripts\replace_order.py --order-id <order-id> --order-file replacement.json --account-hash <hash> --confirm-live-order
```

## Rules

- Default output is JSON only; it is not submitted.
- Preview with Schwab before live placement when practical.
- Live place, cancel, and replace require `--confirm-live-order`.
- Use `src/schwab_py_skills/orders/builder.py` for uncommon raw order JSON.
- Use strategy helpers for vertical spreads, iron condors, bracket, OCO, trigger, straddle, strangle, and covered call patterns.
- Use `docs/ORDER_STRATEGY_EXAMPLES.md` for concrete strategy examples and assumptions.
