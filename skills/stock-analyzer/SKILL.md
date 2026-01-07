---
description: Specialized skill for financial stock analysis, technicals, and market intelligence
capabilities: ["stock analysis", "chart generation", "sentiment analysis", "technical indicators", "financial data"]
---

# Stock Analyzer

A specialized skill designed to provide in-depth financial stock analysis. It uses `yfinance` & `mplfinance` to fetch real-time market data, generate charts, calculate technical indicators, and analyze news sentiment.

## Capabilities
- **Latest Data**: Recent price history with Open, High, Low, Close, Volume.
- **Chart Generation**: 
    - **Visual Analysis**: Generates professional candlestick charts with SMAs.
    - **Output**: Returns a path to the chart image (PNG).
- **Technical Analysis**: RSI, SMA (50/200), and Volume trends.
- **Sentiment Analysis**:
    - **Headlines**: Latest news events.
    - **Scores**: Polarity (-1 to 1) and Subjectivity for each headline and an average for the stock.
- **Financial Health**: Market Cap, PE Ratio, Revenue, Net Income.

## Tools & Usage

This skill includes a Python script to fetch comprehensive stock data.

### How to fetch stock data
When the user asks for analysis (e.g., "Analyze AAPL", "Chart for TSLA", "Sentiment for NVDA"), **you must first run the data fetching script**.

Run the following command:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/fetch_stock.py <TICKER>
```
*Optional arguments:*
- `--period <1mo|6mo|1y|max>`: Time range (default: 1mo).
- `--interval <1d|1wk|1mo>`: Candle interval (default: 1d).

**Output Handling:**
- **Chart**: The JSON output includes a `"chart"` field with a file path. **You must display this image** to the user using markdown: `![Chart](<path>)`.
- **Sentiment**: Use the values in `"news_sentiment"` to describe market mood.

**Workflow:**
1.  **Identify Intent**: Chart? Sentiment? Full Analysis?
2.  **Fetch Data**: Run `fetch_stock.py`.
3.  **Analyze**: 
    - **Display Chart**: Embed the image found in `data['chart']`.
    - **Summarize Sentiment**: "Average news sentiment is Positive (0.45)..."
    - **Technical/Fundamental**: Synthesize indicators and financials.
4.  **Report**: Present a holistic view (Visuals + Data + Text).

## Context and examples
- "Show me a chart of AAPL" -> *Run script, display `data['chart']`*
- "What is the sentiment for Tesla?" -> *Run script, report `data['news_sentiment']`*
- "Analyze NVDA fundamentals" -> *Run script, report financials + PE*
