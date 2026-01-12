---
description: Skill for backtesting and evaluating trading strategies on historical stock data
capabilities: ["backtesting", "strategy evaluation", "performance metrics", "chart generation"]
---

# Trading Strategy

A skill for backtesting specific trading strategies, evaluating their performance, and visualizing entry/exit points.

## Capabilities
- **Backtesting**: Simulate trading strategies on historical data
- **Strategy Library**:
    - `sma_crossover`: Buy when Fast SMA > Slow SMA
    - `rsi_reversal`: Contrarion strategy based on RSI overbought/oversold levels
- **Performance Metrics**:
    - Total Return
    - Annualized Return
    - Win Rate
    - Max Drawdown
    - Sharpe Ratio
- **Visualization**: Generates charts with Buy/Sell markers

## Workflow

### 1. Run Backtest
Users specify a ticker, strategy, and time period.

**Example**:
- "Test SMA crossover on AAPL for the last 2 years" -> `python3 ${CLAUDE_PLUGIN_ROOT}/skills/trading-strategy/scripts/main.py --ticker AAPL --strategy sma_crossover --period 2y`

### 2. Parse Output
The script returns a JSON object with:
- `metrics`: Performance summary
- `trades`: List of executed trades
- `chart`: Path to the visualization image

## Command Options

```bash
# Basic SMA Crossover backtest
python3 main.py --ticker AAPL --strategy sma_crossover

# RSI Reversal with custom capital
python3 main.py --ticker TSLA --strategy rsi_reversal --initial-capital 50000

# Custom period
python3 main.py --ticker MSFT --strategy sma_crossover --period 5y
```

## Strategies Details

### SMA Crossover
- **Logic**: 
    - Buy when SMA(Fast) crosses above SMA(Slow)
    - Sell when SMA(Fast) crosses below SMA(Slow)
- **Parameters** (Default):
    - Fast Period: 50
    - Slow Period: 200

### RSI Reversal
- **Logic**:
    - Buy when RSI < 30 (Oversold) AND RSI increases (turns up)
    - Sell when RSI > 70 (Overbought) AND RSI decreases (turns down)
- **Parameters** (Default):
    - RSI Period: 14
