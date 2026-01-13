---
description: Skill for analyzing stock portfolios, assessing risk, and providing actionable suggestions
capabilities: ["portfolio analysis", "risk assessment", "rebalancing suggestions", "profit/loss tracking"]
---

# Portfolio Advisor

A skill that analyzes a user's stock portfolio to provide insights on performance, diversification, and risk management.

## Capabilities
- **Valuation**: Calculate total portfolio value and daily change.
- **Performance**: Track Unrealized P/L for each position and the total portfolio.
- **Risk Assessment**:
    - **Concentration Risk**: Alerts if a single stock makes up > 20% of the portfolio.
    - **Stop Loss**: Alerts if a position is down > 15%.
- **Actionable Suggestions**:
    - Profit taking recommendations for high flyers (>50% gain).
    - Rebalancing suggestions.

## Workflow

### 1. Prepare Portfolio JSON
Create a JSON file with your current holdings:
```json
[
  {"ticker": "AAPL", "quantity": 10, "cost_basis": 150.0},
  {"ticker": "MSFT", "quantity": 5, "cost_basis": 300.0}
]
```

### 2. Run Analysis
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/portfolio-advisor/scripts/main.py --portfolio /path/to/portfolio.json
```

### 3. Review Output
The output JSON will contain:
- `summary`: Total value, Total P/L
- `holdings`: Detailed per-stock analysis
- `suggestions`: List of warnings and opportunities
- `metrics`: Diversification stats

## Command Options

```bash
# Analyze portfolio
python3 main.py --portfolio my_holdings.json

# Analyze and save report (standard redirection)
python3 main.py --portfolio my_holdings.json > report.json
```
