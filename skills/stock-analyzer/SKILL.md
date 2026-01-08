---
description: Specialized skill for financial stock analysis, technical indicators, chart generation, sentiment analysis, and market intelligence
capabilities: ["stock analysis", "chart generation", "sentiment analysis", "technical indicators", "trading signals", "financial data", "multi-market support"]
---

# Stock Analyzer

A comprehensive skill for financial stock analysis with technical indicators, real-time data fetching, chart generation, sentiment analysis, and multi-market support.

## Capabilities
- **Real-Time Data**: Fetch current prices and historical data from multiple sources
- **Chart Generation**:
    - **Visual Analysis**: Generates professional candlestick charts with SMAs
    - **Output**: Returns a path to the chart image (PNG)
- **Technical Analysis**: 15+ indicators (RSI, MACD, Bollinger Bands, Moving Averages, etc.)
- **Trading Signals**: Automated buy/sell/hold recommendations based on technical indicators
- **Sentiment Analysis**:
    - **Headlines**: Latest news events
    - **Scores**: Polarity (-1 to 1) and Subjectivity for each headline and an average for the stock
- **Financial Health**: Market Cap, PE Ratio, Revenue, Net Income
- **Multi-Market Support**: US stocks, Hong Kong stocks (.HK), China A-shares (.SS, .SZ)
- **Data Caching**: Automatic caching to reduce API calls and improve response time

## Technical Indicators

**Trend Indicators:**
- Simple Moving Averages (SMA): 20, 50, 200-day
- Exponential Moving Averages (EMA): 12, 26-day
- MACD (Moving Average Convergence Divergence)
- ADX (Average Directional Index)

**Momentum Indicators:**
- RSI (Relative Strength Index)
- Stochastic Oscillator (%K, %D)
- CCI (Commodity Channel Index)
- ROC (Rate of Change)

**Volatility Indicators:**
- Bollinger Bands (Upper, Middle, Lower, Bandwidth)
- ATR (Average True Range)
- Standard Deviation

**Volume Indicators:**
- OBV (On-Balance Volume)
- VWAP (Volume Weighted Average Price)

## Trading Signals

The skill generates the following signals:
- **RSI Signal**: Overbought (>70), Oversold (<30), Neutral
- **MACD Signal**: Bullish, Bearish, Neutral
- **Bollinger Bands Signal**: Overbought, Oversold, Normal
- **Trend Signal**: Strong Uptrend, Uptrend, Downtrend, Strong Downtrend, Sideways
- **Stochastic Signal**: Overbought, Oversold, Neutral
- **Volume Signal**: High, Low, Normal
- **Overall Recommendation**: Strong Buy, Buy, Hold, Sell, Strong Sell

## Workflow

When a user requests stock analysis, follow this workflow:

### 1. Identify Analysis Type

**Basic price queries:**
- "What's AAPL trading at?" → Run: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker AAPL`
- "Show me Tesla's price" → Run: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker TSLA`

**Technical analysis queries:**
- "Is AAPL overbought?" → Run: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker AAPL --technical`
- "Analyze TSLA with technical indicators" → Run: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker TSLA --technical`
- "Should I buy MSFT?" → Run: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker MSFT --technical`

**Chart generation queries:**
- "Show me a chart of AAPL" → Run script with chart option, display the image from `data['chart']` field
- "Chart for NVDA" → Generate candlestick chart and embed using `![Chart](<path>)`

**Sentiment analysis queries:**
- "What is the sentiment for Tesla?" → Run script and report `data['news_sentiment']` values
- "How is the news for NVDA?" → Analyze sentiment scores and describe market mood

**Historical data queries:**
- "Show me AAPL's 6-month trend" → Run: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker AAPL --period 6mo --technical`

**Multi-market queries:**
- "Analyze Tencent stock" → Run: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker 0700.HK --technical`
- "How is Moutai performing?" → Run: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker 600519.SS --technical`

### 2. Parse JSON Output

The script returns structured JSON with the following format:

```json
{
  "metadata": {
    "ticker": "AAPL",
    "market": "us",
    "timestamp": "2026-01-07T10:30:00Z",
    "currency": "USD",
    "cached": false
  },
  "price": {
    "current": 185.23,
    "change": 0.73,
    "change_pct": 0.40,
    "open": 184.50,
    "high": 186.00,
    "low": 183.75,
    "volume": 52341000
  },
  "technical": {
    "indicators": {
      "rsi_14": 62.5,
      "macd": {"macd": 2.34, "signal": 1.89, "histogram": 0.45},
      "bb_upper": 190.50,
      "bb_middle": 185.00,
      "bb_lower": 179.50,
      "sma_20": 183.20,
      "sma_50": 182.34,
      "sma_200": 175.67
    },
    "signals": {
      "rsi_signal": "neutral",
      "macd_signal": "bullish",
      "bb_signal": "normal",
      "trend": "uptrend",
      "recommendation": "buy"
    }
  },
  "chart": "/path/to/chart.png",
  "news_sentiment": {
    "average_polarity": 0.45,
    "average_subjectivity": 0.62,
    "headlines": [...]
  },
  "history": [...]
}
```

### 3. Provide Analysis

Based on the data returned:

**For price-only queries:**
- State current price, change, and change percentage
- Mention if data is cached (check metadata.cached)

**For technical analysis queries:**
- Interpret key indicators relevant to the question
- Explain what the signals mean
- Provide the overall recommendation
- Support your analysis with specific indicator values

**For chart queries:**
- **Display the chart**: The JSON output includes a `"chart"` field with a file path. **You must display this image** to the user using markdown: `![Chart](<path>)`
- Describe key visual patterns visible in the chart

**For sentiment queries:**
- Use the values in `"news_sentiment"` to describe market mood
- Report average polarity and subjectivity
- Mention key headlines if relevant

**Example interpretation:**
```
User: "Is AAPL overbought right now?"

[After running the command and getting JSON output]

Response: "Apple (AAPL) is currently trading at $185.23, up 0.40% today. Based on technical analysis:

- RSI is at 62.5, which is in neutral territory (not overbought). Overbought would be above 70.
- The price is near the middle Bollinger Band at $185.00, suggesting normal volatility.
- MACD shows a bullish signal with a positive histogram of 0.45.
- The stock is in an uptrend, trading above its 50-day SMA of $182.34.

Overall recommendation: BUY. The stock shows bullish momentum without being overextended."
```

### 4. Multi-Market Support

The skill automatically detects the market from the ticker format:

- **US Stocks**: Use standard ticker (AAPL, TSLA, MSFT)
- **Hong Kong Stocks**: Use .HK suffix (0700.HK for Tencent, 9988.HK for Alibaba)
- **China A-Shares**:
  - Shanghai: .SS suffix (600519.SS for Moutai)
  - Shenzhen: .SZ suffix (000001.SZ for Ping An Bank)

The system automatically adjusts timezone and currency based on the market.

## Command Options

```bash
# Basic price check
python3 main.py --ticker AAPL

# Technical analysis
python3 main.py --ticker AAPL --technical

# Custom time period (1mo, 6mo, 1y, max)
python3 main.py --ticker AAPL --period 3mo --technical

# Custom interval (1d, 1wk, 1mo)
python3 main.py --ticker AAPL --period 6mo --interval 1d

# Disable caching (force fresh data)
python3 main.py --ticker AAPL --technical --no-cache
```

## Important Notes

1. **Always use `${CLAUDE_PLUGIN_ROOT}`** - This environment variable points to the correct plugin directory
2. **Check for errors** - If the JSON contains an `error` field, explain the error to the user
3. **Cache awareness** - Mention if data is cached (metadata.cached = true) when relevant
4. **Market context** - Include market name and currency in your response
5. **Be specific** - Cite actual indicator values from the JSON, don't make up numbers
6. **Explain signals** - Don't just state "RSI is 62.5", explain what that means ("RSI at 62.5 indicates neutral momentum, neither overbought nor oversold")
7. **Display charts** - When chart data is available, always embed the image in your response
8. **Report sentiment** - Include news sentiment analysis when available in the data

## Error Handling

If the command fails or returns an error:
1. Check the error message in the JSON output
2. Common issues:
   - Invalid ticker symbol
   - Market closed (recent data may not be available)
   - API rate limits (try again with --no-cache)
   - Network issues
3. Explain the error clearly to the user
4. Suggest alternatives if possible

## Examples

**Example 1: Basic Price Check**
```
User: "What's the current price of Apple stock?"

Command: python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker AAPL

Response: "Apple (AAPL) is currently trading at $185.23 USD, up $0.73 (0.40%) today."
```

**Example 2: Technical Analysis**
```
User: "Should I buy Tesla stock?"

Command: python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker TSLA --technical

Response: "Tesla (TSLA) is trading at $235.50. Based on technical analysis:
- RSI: 45.2 (neutral - neither overbought nor oversold)
- MACD: Bullish signal (histogram: +1.23)
- Trend: Uptrend (price above 50-day SMA)
- Bollinger Bands: Trading in normal range

Overall recommendation: BUY. The stock shows bullish momentum with neutral RSI, suggesting room for upside without being overextended."
```

**Example 3: Chart Generation**
```
User: "Show me a chart of AAPL"

Command: python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker AAPL

Response: "Here's the candlestick chart for Apple (AAPL):
![Chart](/path/to/chart.png)

The chart shows recent price action with 50-day and 200-day moving averages overlaid."
```

**Example 4: Sentiment Analysis**
```
User: "What is the sentiment for Tesla?"

Command: python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker TSLA

Response: "Tesla (TSLA) news sentiment analysis:
- Average Polarity: 0.45 (Positive)
- Average Subjectivity: 0.62 (Moderately Subjective)

Recent headlines show a generally positive sentiment toward Tesla, indicating favorable market perception."
```

**Example 5: Hong Kong Stock**
```
User: "Analyze Tencent stock"

Command: python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker 0700.HK --technical

Response: "Tencent Holdings (0700.HK) is trading at 385.00 HKD in the Hong Kong market..."
```

**Example 6: Historical Trend**
```
User: "How has Microsoft performed over the last 6 months?"

Command: python3 ${CLAUDE_PLUGIN_ROOT}/skills/stock-analyzer/scripts/main.py --ticker MSFT --period 6mo --technical

Response: "Microsoft (MSFT) is currently at $420.15. Over the past 6 months:
- Strong uptrend: Price well above 200-day SMA ($380.25)
- RSI at 68: Approaching overbought but still in bullish territory
- MACD: Positive and rising
The stock has gained approximately 11% over the 6-month period, showing consistent upward momentum."
```

## Data Sources

- **Primary**: yfinance library (Yahoo Finance data)
- **Fallback**: Direct Yahoo Finance API
- **Cache**: Local file-based cache (15-minute TTL)

## Limitations

- Real-time data has ~15-minute delay for free tier
- Some indicators require minimum data history (e.g., 200-day SMA needs 200 days)
- Market-specific data availability varies (US > HK > CN A-shares)
- Technical analysis is based on historical data and doesn't guarantee future performance
