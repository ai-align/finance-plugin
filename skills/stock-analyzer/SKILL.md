---
description: Specialized skill for financial stock analysis, technicals, and market intelligence
capabilities: ["stock analysis", "technical indicators", "financial data", "market news"]
---

# Stock Analyzer

A specialized skill designed to provide in-depth financial stock analysis. It uses `yfinance` to fetch real-time market data, technical indicators, and news.

## Capabilities
- **Latest Data**: Recent price history with Open, High, Low, Close, Volume.
- **Technical Analysis**: 
    - **RSI (Relative Strength Index)**: Detect overbought (>70) or oversold (<30) conditions.
    - **Moving Averages (SMA)**: 50-day and 200-day trends.
- **Fundamental Insights**: Market Cap, PE Ratio, Dividend Yield.
- **Financial Health**: Key metrics from Income Statement (Revenue, Net Income).
- **Market Context**: Latest news headlines for the stock.

## Tools & Usage

This skill includes a Python script to fetch comprehensive stock data.

### How to fetch stock data
When the user asks for analysis of a specific stock (e.g., "Analyze AAPL", "Check RSI for TSLA"), **you must first run the data fetching script**.

Run the following command:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/fetch_stock.py <TICKER>
```
*Optional arguments:*
- `--period <1mo|6mo|1y|max>`: Time range for partial history (default: 1mo).
- `--interval <1d|1wk|1mo>`: Candle interval (default: 1d).

**Workflow:**
1.  **Identify Intent**: Does the user want price action, technicals, or fundamental health?
2.  **Fetch Data**: Run `fetch_stock.py`.
3.  **Analyze**: 
    - Check `technicals` for RSI and SMAs.
    - Check `financials` for revenue growth.
    - Check `news` for recent catalysts.
4.  **Report**: Synthesize the data into a clear insight.

## Context and examples
- "Is AAPL overbought?" -> *Check RSI in output*
- "How is Tesla's revenue growth?" -> *Check financials.totalRevenue*
- "Why is NVDA dropping today?" -> *Check news section*
- "Compare price vs 200-day MA" -> *Check history.close vs history.sma_200*
