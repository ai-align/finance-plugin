import sys
import json
import argparse
from datetime import datetime
import pandas as pd

def calculate_rsi(data, window=14):
    """Calculates RSI on a pandas Series."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_stock_data(ticker, period="1mo", interval="1d"):
    """
    Fetches stock data using yfinance.
    Returns a dictionary with symbol, fundamentals, technicals, news, and history.
    """
    try:
        import yfinance as yf
    except ImportError:
        return {
            "error": "yfinance module not found. Please install it via 'pip install -r requirements.txt'"
        }

    try:
        stock = yf.Ticker(ticker)
        
        # 1. Fetch History & Calculate Technicals
        # fetching a bit more data than requested to ensure MA/RSI have enough initial data
        # Always fetch at least 2y to ensure SMA_200 is calculable
        extended_period = "5y" if period in ["5y", "max"] else "2y"
        hist = stock.history(period=extended_period, interval=interval, auto_adjust=True)
        
        if hist.empty:
            return {
                "error": f"No data found for ticker '{ticker}'. It may be delisted or invalid."
            }

        # Calculate Indicators
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
        hist['RSI'] = calculate_rsi(hist['Close'])

        # Filter back to requested period for output
        if period != "max":
            # Approximation: slice the last N days based on period logic or just return the last 30/365 rows
            # yfinance history(period=...) returns exactly that. 
            # We re-fetch or just slice. Let's slice based on roughly the requested period size.
            cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=30 if period=="1mo" else 365)
            # Simple approach: if they asked for 1mo, show last 22 trading days
            if period == '1mo':
                output_hist = hist.tail(22)
            elif period == '5d':
                 output_hist = hist.tail(5)
            elif period == '3mo':
                 output_hist = hist.tail(66)
            elif period == '6mo':
                 output_hist = hist.tail(132)
            elif period == '1y':
                 output_hist = hist.tail(252)
            else:
                 output_hist = hist
        else:
            output_hist = hist

        # Format history
        history_list = []
        for date, row in output_hist.iterrows():
            history_list.append({
                "date": date.strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume']),
                # Include calculated indicators in history if they exist
                "sma_50": round(row['SMA_50'], 2) if pd.notnull(row['SMA_50']) else None,
                "sma_200": round(row['SMA_200'], 2) if pd.notnull(row['SMA_200']) else None,
                "rsi": round(row['RSI'], 2) if pd.notnull(row['RSI']) else None
            })

        # Latest Technical Snapshot
        last_row = hist.iloc[-1]
        technicals = {
            "rsi": round(last_row['RSI'], 2) if pd.notnull(last_row['RSI']) else None,
            "sma_50": round(last_row['SMA_50'], 2) if pd.notnull(last_row['SMA_50']) else None,
            "sma_200": round(last_row['SMA_200'], 2) if pd.notnull(last_row['SMA_200']) else None,
            "52WeekHigh": round(hist['High'].max(), 2),
            "52WeekLow": round(hist['Low'].min(), 2)
        }

        # 2. Fundamentals
        info = stock.info or {}
        fundamentals = {
            "longName": info.get("longName"),
            "sector": info.get("sector"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "dividendYield": info.get("dividendYield"),
            "beta": info.get("beta")
        }

        # 3. Financials (Income Statement Highlights)
        fin_data = {}
        try:
             # financials is a DataFrame
             financials = stock.financials
             if financials is not None and not financials.empty:
                 # Get latest year column
                 latest_date = financials.columns[0]
                 fin_data = {
                     "reportDate": latest_date.strftime('%Y-%m-%d'),
                     "totalRevenue": int(financials.loc['Total Revenue'].iloc[0]) if 'Total Revenue' in financials.index else None,
                     "netIncome": int(financials.loc['Net Income'].iloc[0]) if 'Net Income' in financials.index else None,
                 }
        except Exception:
            pass # Financials might fail or be missing

        # 4. News
        news_list = []
        try:
            raw_news = stock.news
            for item in raw_news[:5]:
                # Handle nested structure (yfinance >= 0.2.x often has 'content')
                content = item.get('content', item) # Fallback to item itself if no content
                
                title = content.get('title')
                pub_date = content.get('pubDate') or content.get('providerPublishTime')
                
                # Link might be in clickThroughUrl object
                link = content.get('link')
                if not link:
                    ctu = content.get('clickThroughUrl')
                    if ctu:
                         link = ctu.get('url')
                
                # Publisher
                publisher = content.get('publisher')
                if not publisher:
                    prov = content.get('provider')
                    if prov:
                        publisher = prov.get('displayName')

                news_list.append({
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "providerPublishTime": str(pub_date) if pub_date else None
                })
        except Exception:
            pass

        return {
            "symbol": ticker.upper(),
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "fundamentals": fundamentals,
            "financials": fin_data,
            "technicals": technicals,
            "news": news_list,
            "history": history_list
        }

    except Exception as e:
        return {
            "error": str(e)
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch advanced stock data using yfinance")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--period", default="1mo", help="Data period to download (default: 1mo)")
    parser.add_argument("--interval", default="1d", help="Data interval (default: 1d)")
    
    args = parser.parse_args()
    
    data = get_stock_data(args.ticker, period=args.period, interval=args.interval)
    print(json.dumps(data, indent=2))
