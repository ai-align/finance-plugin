import sys
import json
import argparse
from datetime import datetime
import tempfile
import os

import pandas as pd
import numpy as np

def calculate_rsi(data, window=14):
    """Calculates RSI on a pandas Series."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data, slow=26, fast=12, signal=9):
    """Calculates MACD, Signal, and Histogram."""
    exp1 = data.ewm(span=fast, adjust=False).mean()
    exp2 = data.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_bollinger_bands(data, window=20, num_std=2):
    """Calculates Bollinger Bands (Upper, Middle, Lower)."""
    sma = data.rolling(window=window).mean()
    std = data.rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return upper, sma, lower

def analyze_sentiment(text):
    """
    Returns polarity (-1 to 1) and subjectivity (0 to 1).
    """
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        return blob.sentiment.polarity, blob.sentiment.subjectivity
    except ImportError:
        return None, None

def generate_chart_image(ticker, hist):
    """
    Generates a multi-panel candlestick chart (Price, Volume, RSI, MACD).
    """
    try:
        import mplfinance as mpf
        
        # Prepare data frame for mplfinance
        df = hist.copy()
        # Ensure capitalization matches what mpf expects
        df.columns = [c.capitalize() for c in df.columns]
        
        # Create temp file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{ticker}_{timestamp}_chart.png"
        filepath = os.path.join(tempfile.gettempdir(), filename)

        # Plots to add
        add_plots = []
        
        # SMA 50/200 on Price Panel (0)
        if 'SMA_50' in hist.columns:
             add_plots.append(mpf.make_addplot(hist['SMA_50'], panel=0, color='orange', width=1.0, label='SMA 50'))
        if 'SMA_200' in hist.columns:
             add_plots.append(mpf.make_addplot(hist['SMA_200'], panel=0, color='blue', width=1.0, label='SMA 200'))
             
        # BBands on Price Panel (0)
        if 'BBU_20_2.0' in hist.columns:
             add_plots.append(mpf.make_addplot(hist['BBU_20_2.0'], panel=0, color='gray', width=0.5, linestyle='dashed'))
             add_plots.append(mpf.make_addplot(hist['BBL_20_2.0'], panel=0, color='gray', width=0.5, linestyle='dashed'))

        # RSI on Panel 2 (Panel 1 is Volume)
        if 'RSI_14' in hist.columns:
             add_plots.append(mpf.make_addplot(hist['RSI_14'], panel=2, color='purple', width=1.0, ylabel='RSI'))
             
        # MACD on Panel 3
        if 'MACD' in hist.columns:
             # Histogram, MACD line, Signal line
             add_plots.append(mpf.make_addplot(hist['MACD_Hist'], type='bar', panel=3, color='dimgray', alpha=0.5, ylabel='MACD'))
             add_plots.append(mpf.make_addplot(hist['MACD'], panel=3, color='fuchsia', width=1.0))
             add_plots.append(mpf.make_addplot(hist['MACD_Signal'], panel=3, color='gold', width=1.0))

        # Plot
        # panel_ratios = (Price, Volume, RSI, MACD)
        mpf.plot(
            df, 
            type='candle', 
            style='yahoo', 
            volume=True, 
            addplot=add_plots, 
            savefig=filepath,
            title=f"{ticker} Technical Analysis",
            tight_layout=True,
            panel_ratios=(4,1,1,1),
            scale_width_adjustment=dict(volume=0.7, candle=1),
            figratio=(12,8),
            figscale=1.2
        )
        return filepath
    except ImportError:
        return None
    except Exception as e:
        return None # Fail silently/gracefully on chart error

def get_signals(last_row):
    """
    Generates trading signals based on technical indicators.
    """
    signals = {
        "rsi_signal": "neutral",
        "macd_signal": "neutral",
        "bb_signal": "normal",
        "trend": "sideways",
        "recommendation": "hold"
    }
    
    # RSI
    rsi = last_row.get('RSI_14')
    if pd.notnull(rsi):
        if rsi > 70: signals['rsi_signal'] = 'overbought'
        elif rsi < 30: signals['rsi_signal'] = 'oversold'

    # MACD
    macd = last_row.get('MACD')
    signal = last_row.get('MACD_Signal')
    if pd.notnull(macd) and pd.notnull(signal):
        if macd > signal: signals['macd_signal'] = 'bullish'
        elif macd < signal: signals['macd_signal'] = 'bearish'

    # Bollinger Bands
    price = last_row['Close']
    bb_upper = last_row.get('BBU_20_2.0')
    bb_lower = last_row.get('BBL_20_2.0')
    if pd.notnull(bb_upper) and price > bb_upper: signals['bb_signal'] = 'overbought'
    elif pd.notnull(bb_lower) and price < bb_lower: signals['bb_signal'] = 'oversold'

    # Trend (Price vs SMA 50)
    sma_50 = last_row.get('SMA_50')
    if pd.notnull(sma_50):
        if price > sma_50 * 1.02: signals['trend'] = 'uptrend'
        elif price < sma_50 * 0.98: signals['trend'] = 'downtrend'

    # Overall Recommendation
    score = 0
    if signals['rsi_signal'] == 'oversold': score += 2
    elif signals['rsi_signal'] == 'overbought': score -= 2
    
    if signals['macd_signal'] == 'bullish': score += 1
    elif signals['macd_signal'] == 'bearish': score -= 1
    
    if signals['bb_signal'] == 'oversold': score += 1
    elif signals['bb_signal'] == 'overbought': score -= 1
    
    if signals['trend'] == 'uptrend': score += 1
    elif signals['trend'] == 'downtrend': score -= 1

    if score >= 3: signals['recommendation'] = "strong buy"
    elif score >= 1: signals['recommendation'] = "buy"
    elif score <= -3: signals['recommendation'] = "strong sell"
    elif score <= -1: signals['recommendation'] = "sell"
    
    return signals

def get_stock_data(ticker, period="1mo", interval="1d", technical=False, no_cache=False):
    try:
        import yfinance as yf
    except ImportError as e:
        return {"error": f"Missing dependency: {str(e)}"}

    try:
        stock = yf.Ticker(ticker)
        
        # Fetch extended history for calculations
        # Always fetch at least 1y for decent indicators, unless period is max
        fetch_period = "2y" if period in ["1y", "2y", "5y", "max"] else "1y"
        if period == "max": fetch_period = "max"
        
        hist = stock.history(period=fetch_period, interval=interval, auto_adjust=True)
        
        if hist.empty:
            return {"error": f"No data found for ticker '{ticker}'"}

        # Calculate Indicators Manually (Replacing pandas-ta)
        
        # 1. Moving Averages
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
        
        # 2. RSI
        hist['RSI_14'] = calculate_rsi(hist['Close'])
        
        # 3. MACD
        hist['MACD'], hist['MACD_Signal'], hist['MACD_Hist'] = calculate_macd(hist['Close'])
        
        # 4. Bollinger Bands
        hist['BBU_20_2.0'], hist['BBM_20_2.0'], hist['BBL_20_2.0'] = calculate_bollinger_bands(hist['Close'])

        # Slice for output
        if period != "max":
            # Rough slicing based on trading days
            days_map = {'5d': 5, '1mo': 22, '3mo': 66, '6mo': 132, '1y': 252, '2y': 504, '5y': 1260}
            rows = days_map.get(period, 22)
            output_hist = hist.tail(rows)
        else:
            output_hist = hist

        # Generate Chart
        chart_path = generate_chart_image(ticker, output_hist)
        
        # Signals (based on latest full candle)
        last_row = hist.iloc[-1]
        signals = get_signals(last_row)

        # Format History Output
        history_list = []
        for date, row in output_hist.iterrows():
            item = {
                "date": date.strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            }
            # Add technicals to history if requested
            if technical:
                 if pd.notnull(row.get('RSI_14')): item['rsi_14'] = round(row['RSI_14'], 2)
                 if pd.notnull(row.get('SMA_50')): item['sma_50'] = round(row['SMA_50'], 2)
                 if pd.notnull(row.get('SMA_200')): item['sma_200'] = round(row['SMA_200'], 2)
            history_list.append(item)

        # Latest Technical Snapshot
        tech_indicators = {
            "rsi_14": round(last_row['RSI_14'], 2) if pd.notnull(last_row.get('RSI_14')) else None,
            "macd": {
                "macd": round(last_row['MACD'], 3) if pd.notnull(last_row.get('MACD')) else None,
                "signal": round(last_row['MACD_Signal'], 3) if pd.notnull(last_row.get('MACD_Signal')) else None,
                "histogram": round(last_row['MACD_Hist'], 3) if pd.notnull(last_row.get('MACD_Hist')) else None
            },
            "bb_upper": round(last_row['BBU_20_2.0'], 2) if pd.notnull(last_row.get('BBU_20_2.0')) else None,
            "bb_middle": round(last_row['BBM_20_2.0'], 2) if pd.notnull(last_row.get('BBM_20_2.0')) else None,
            "bb_lower": round(last_row['BBL_20_2.0'], 2) if pd.notnull(last_row.get('BBL_20_2.0')) else None,
            "sma_20": round(last_row['SMA_20'], 2) if pd.notnull(last_row.get('SMA_20')) else None,
            "sma_50": round(last_row['SMA_50'], 2) if pd.notnull(last_row.get('SMA_50')) else None,
            "sma_200": round(last_row['SMA_200'], 2) if pd.notnull(last_row.get('SMA_200')) else None
        }

        # News & Sentiment
        news_sentiment = {"average_polarity": 0, "average_subjectivity": 0, "headlines": []}
        try:
            raw_news = stock.news
            scores_pol = []
            scores_sub = []
            for item in raw_news[:5]:
                content = item.get('content', item)
                title = content.get('title')
                pol, sub = analyze_sentiment(title)
                
                if pol is not None:
                     scores_pol.append(pol)
                     scores_sub.append(sub)
                
                news_sentiment['headlines'].append({
                    "title": title,
                    "polarity": round(pol, 2) if pol else 0
                })
            
            if scores_pol:
                news_sentiment['average_polarity'] = round(sum(scores_pol) / len(scores_pol), 2)
                news_sentiment['average_subjectivity'] = round(sum(scores_sub) / len(scores_sub), 2)
        except Exception:
            pass

        # Final Price Object
        price_obj = {
            "current": round(last_row['Close'], 2),
            "change": round(last_row['Close'] - last_row['Open'], 2), 
            "change_pct": round((last_row['Close'] - last_row['Open']) / last_row['Open'] * 100, 2),
            "open": round(last_row['Open'], 2),
            "high": round(last_row['High'], 2),
            "low": round(last_row['Low'], 2),
            "volume": int(last_row['Volume'])
        }

        # Metadata / Info
        info = stock.info or {}
        currency = info.get('currency', 'USD')
        
        # Infer market
        market = 'us'
        if ticker.endswith('.HK'): market = 'hk'
        elif ticker.endswith('.SS') or ticker.endswith('.SZ'): market = 'cn'
        elif ticker.endswith('.L'): market = 'uk'
        
        return {
            "metadata": {
                "ticker": ticker.upper(),
                "market": market,
                "currency": currency,
                "timestamp": datetime.now().isoformat(),
                "cached": False 
            },
            "price": price_obj,
            "technical": {
                "indicators": tech_indicators,
                "signals": signals
            },
            "chart": chart_path,
            "news_sentiment": news_sentiment,
            "history": history_list
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Analyzer Main Script")
    parser.add_argument("--ticker", required=True, help="Stock ticker symbol")
    parser.add_argument("--period", default="1mo", help="Data period (1mo, 6mo, 1y, max)")
    parser.add_argument("--interval", default="1d", help="Data interval (1d, 1wk, 1mo)")
    parser.add_argument("--technical", action="store_true", help="Include technical analysis")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    
    args = parser.parse_args()
    
    data = get_stock_data(args.ticker, period=args.period, interval=args.interval, technical=args.technical, no_cache=args.no_cache)
    print(json.dumps(data, indent=2))
