---
name: schwab-portfolio
description: Use when retrieving Schwab account hashes, balances, positions, transactions, linked accounts, or order history through schwab-py.
---

# Schwab Portfolio

Use this skill for account and portfolio inspection.

## Positions

```powershell
python scripts\get_portfolio.py --positions
python scripts\get_portfolio.py --all-linked --positions
python scripts\get_transactions.py --symbol AAPL --transaction-type trade
python scripts\get_orders.py --status filled --max-results 10
python scripts\get_order.py --order-id <order-id> --account-hash <hash>
```

Use an explicit hash when available:

```powershell
python scripts\get_portfolio.py --account-hash <hash> --positions
```

## Rules

- Use `schwab-py` directly.
- Redact account numbers and hashes in chat summaries by default.
- Do not place or modify orders from this skill.
- If auth fails, run `python -m schwab_py_skills.setup_env --show` before deeper debugging.
