---
description: Specialized skill for financial stock analysis and market insights
capabilities: ["stock analysis", "financial evaluation", "market trends"]
---

# Stock Analyzer

A specialized skill designed to provide in-depth financial stock analysis. It includes a built-in script to fetch real-time market data to support your analysis.

## Capabilities
- **Data Retrieval**: Fetch real-time stock prices and historical data using the provided tool script.
- **Technical Analysis**: Interpret technical indicators (Moving Averages, RSI, MACD) based on fresh data.
- **Fundamental Analysis**: Evaluate financial health using balance sheets and income statements.
- **Market Trends**: Analyze broader market movements and sector performance.

## Tools & Usage

This skill includes a Python script to fetch stock data.

### How to fetch stock data
When the user asks for analysis of a specific stock (e.g., "Analyze AAPL"), **you must first run the data fetching script** to get the latest prices.

Run the following command:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/fetch_stock.py <TICKER>
```
*Replace `<TICKER>` with the stock symbol (e.g., AAPL, TSLA).*

**Workflow:**
1.  **Identify Ticker**: Extract the stock symbol from the user's request.
2.  **Fetch Data**: Run the `fetch_stock.py` script.
3.  **Analyze**: Parse the JSON output and perform your analysis (technical/fundamental) based on the returned data.
4.  **Report**: Present the findings to the user, citing the current price and recent trends.

## Context and examples
Use this skill when the user asks for:
- "Analyze the recent performance of AAPL" -> *Run script for AAPL*
- "How is Tesla doing today?" -> *Run script for TSLA*
- "Compare the price movement of BTC-USD" -> *Run script for BTC-USD*

This skill is best used for quantitative assessments supported by real data.
