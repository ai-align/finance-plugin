import argparse
import json
import sys
import tempfile
import os
from datetime import datetime

import pandas as pd
import numpy as np

def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_backtest(df, strategy, initial_capital):
    cash = initial_capital
    position = 0
    trades = []
    equity_curve = []
    
    # Pre-calculate indicators
    if strategy == 'sma_crossover':
        df['SMA_Fast'] = calculate_sma(df['Close'], 50)
        df['SMA_Slow'] = calculate_sma(df['Close'], 200)
    elif strategy == 'rsi_reversal':
        df['RSI'] = calculate_rsi(df['Close'], 14)

    # Simulation loop
    # We iterate from the start but need enough data for indicators
    start_idx = 200 if strategy == 'sma_crossover' else 15
    
    for i in range(start_idx, len(df)):
        price = df['Close'].iloc[i]
        date = df.index[i]
        
        signal = 0 # 0: Hold, 1: Buy, -1: Sell
        
        # Strategy Logic
        if strategy == 'sma_crossover':
            # Check for crossover
            curr_fast = df['SMA_Fast'].iloc[i]
            curr_slow = df['SMA_Slow'].iloc[i]
            prev_fast = df['SMA_Fast'].iloc[i-1]
            prev_slow = df['SMA_Slow'].iloc[i-1]
            
            if prev_fast <= prev_slow and curr_fast > curr_slow:
                signal = 1
            elif prev_fast >= prev_slow and curr_fast < curr_slow:
                signal = -1
                
        elif strategy == 'rsi_reversal':
            curr_rsi = df['RSI'].iloc[i]
            prev_rsi = df['RSI'].iloc[i-1]
            
            # Buy: Oversold and turning up
            if prev_rsi < 30 and curr_rsi > prev_rsi:
                 signal = 1
            # Sell: Overbought and turning down
            elif prev_rsi > 70 and curr_rsi < prev_rsi:
                 signal = -1

        # Execution
        if signal == 1 and position == 0:
            # Buy
            shares = int(cash / price)
            if shares > 0:
                cost = shares * price
                cash -= cost
                position = shares
                trades.append({
                    "type": "buy",
                    "date": date.strftime('%Y-%m-%d'),
                    "price": round(price, 2),
                    "shares": shares,
                    "value": round(cost, 2)
                })
        elif signal == -1 and position > 0:
            # Sell
            proceeds = position * price
            cash += proceeds
            trades.append({
                "type": "sell",
                "date": date.strftime('%Y-%m-%d'),
                "price": round(price, 2),
                "shares": position,
                "value": round(proceeds, 2),
                "profit": round(proceeds - trades[-1]['value'], 2)
            })
            position = 0
            
        # Update Equity
        current_equity = cash + (position * price)
        equity_curve.append(current_equity)

    # Final Value
    final_equity = equity_curve[-1] if equity_curve else initial_capital
    
    return {
        "final_equity": final_equity,
        "trades": trades,
        "equity_curve": equity_curve,
        "data": df  # Return df for charting
    }

def generate_chart(ticker, df, trades, strategy):
    try:
        import mplfinance as mpf
        
        # Filter data to matching length of simulation (if needed) or just last portion
        # But we want to show the trades
        
        # Prepare markers
        buy_indices = []
        sell_indices = []
        
        # Map trade dates to dataframe indices
        # This is a bit tricky if dates are not exact, but we used df index dates
        
        # Create a marker column
        df['Buy_Marker'] = np.nan
        df['Sell_Marker'] = np.nan
        
        for trade in trades:
            date_str = trade['date']
            price = trade['price']
            # Find closest index? Exact match should work if data hasn't changed
            try:
                date_dt = pd.Timestamp(date_str)
                # If date exists in index
                if date_dt in df.index:
                    if trade['type'] == 'buy':
                        df.at[date_dt, 'Buy_Marker'] = price * 0.98 # Place below
                    elif trade['type'] == 'sell':
                        df.at[date_dt, 'Sell_Marker'] = price * 1.02 # Place above
            except:
                pass

        # Plots
        add_plots = []
        
        # Indicators
        if strategy == 'sma_crossover':
            if 'SMA_Fast' in df.columns:
                add_plots.append(mpf.make_addplot(df['SMA_Fast'], color='orange', width=1.0))
            if 'SMA_Slow' in df.columns:
                add_plots.append(mpf.make_addplot(df['SMA_Slow'], color='blue', width=1.0))
        elif strategy == 'rsi_reversal':
             if 'RSI' in df.columns:
                add_plots.append(mpf.make_addplot(df['RSI'], panel=2, color='purple', ylabel='RSI'))

        # Markers
        # We need to make sure we don't pass empty arrays if no trades
        # But mpf expects series matching dataframe length with NaNs for no marker
        
        # If we have trades, add the plots
        if not df['Buy_Marker'].isna().all():
             add_plots.append(mpf.make_addplot(df['Buy_Marker'], type='scatter', markersize=100, marker='^', color='green'))
        if not df['Sell_Marker'].isna().all():
             add_plots.append(mpf.make_addplot(df['Sell_Marker'], type='scatter', markersize=100, marker='v', color='red'))

        # Create temp file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{ticker}_{strategy}_{timestamp}.png"
        filepath = os.path.join(tempfile.gettempdir(), filename)

        mpf.plot(
            df,
            type='candle',
            style='yahoo',
            volume=True,
            addplot=add_plots,
            savefig=filepath,
            title=f"{ticker} - {strategy}",
            tight_layout=True,
            panel_ratios=(4,1,1) if strategy == 'rsi_reversal' else (4,1),
            figratio=(12,8)
        )
        return filepath
    except Exception as e:
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--strategy", required=True, choices=['sma_crossover', 'rsi_reversal'])
    parser.add_argument("--period", default="2y")
    parser.add_argument("--initial-capital", type=float, default=10000.0)
    
    args = parser.parse_args()
    
    try:
        import yfinance as yf
    except ImportError as e:
        print(json.dumps({"error": f"Missing dependency: {str(e)}"}))
        return

    # Fetch Data
    # Ensure enough history for 200 SMA
    fetch_period = args.period
    if args.strategy == 'sma_crossover' and args.period in ['1mo', '3mo', '6mo', '1y']:
         fetch_period = "2y" # Force at least 2y for SMA 200 to settle
         
    stock = yf.Ticker(args.ticker)
    df = stock.history(period=fetch_period, interval="1d", auto_adjust=True)
    
    if df.empty:
        print(json.dumps({"error": f"No data for {args.ticker}"}))
        return

    # Run Backtest
    result = run_backtest(df.copy(), args.strategy, args.initial_capital)
    
    # Calculate Metrics
    total_return = result['final_equity'] - args.initial_capital
    total_return_pct = (total_return / args.initial_capital) * 100
    
    wins = [t for t in result['trades'] if t.get('profit', 0) > 0]
    sell_trades = [t for t in result['trades'] if t['type'] == 'sell']
    win_rate = (len(wins) / len(sell_trades)) * 100 if sell_trades else 0
    
    # Generate Chart
    chart_path = generate_chart(args.ticker, result['data'], result['trades'], args.strategy)
    
    output = {
        "metadata": {
            "ticker": args.ticker,
            "strategy": args.strategy,
            "period": args.period,
            "initial_capital": args.initial_capital
        },
        "metrics": {
            "final_equity": round(result['final_equity'], 2),
            "total_return": round(total_return, 2),
            "total_return_pct": round(total_return_pct, 2),
            "total_trades": len(result['trades']),
            "win_rate": round(win_rate, 2)
        },
        "trades": result['trades'],
        "chart": chart_path
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
