# Schwab-Py Skills Inventory

| Skill | Purpose | Installed Path After Deploy |
|---|---|---|
| `schwab-setup` | Inspect and configure Schwab env vars and token path readiness. | `%USERPROFILE%\.codex\skills\schwab-setup\SKILL.md` |
| `schwab-auth-client` | Verify token, client, and account-hash readiness. | `%USERPROFILE%\.codex\skills\schwab-auth-client\SKILL.md` |
| `schwab-market-data` | Fetch quotes, fundamentals, options chains, price history, movers, and market hours. | `%USERPROFILE%\.codex\skills\schwab-market-data\SKILL.md` |
| `schwab-portfolio` | Inspect linked accounts, positions, transactions, and order history. | `%USERPROFILE%\.codex\skills\schwab-portfolio\SKILL.md` |
| `schwab-orders` | Build dry-run order JSON, preview orders, and perform explicitly confirmed live order maintenance. | `%USERPROFILE%\.codex\skills\schwab-orders\SKILL.md` |
| `schwab-streaming` | Run bounded Schwab streaming sessions for quotes, charts, books, screeners, and account activity. | `%USERPROFILE%\.codex\skills\schwab-streaming\SKILL.md` |

Deploy all skills:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\deploy-skills.ps1
```

Deploy one skill:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\deploy-skills.ps1 -Skills schwab-market-data
```
