import sys
import json
import argparse
from datetime import datetime
import tempfile
import os

import pandas as pd

def calculate_rsi(data, window=14):
    """Calculates RSI on a pandas Series."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def generate_chart_image(ticker, hist, sma_50_col, sma_200_col):
    """
    Generates a candlestick chart with SMAs and returns the path to the temporary image file.
    """
    try:
        import mplfinance as mpf
        
        # Prepare data frame for mplfinance
        # It expects index to be DatetimeIndex and columns Open, High, Low, Close, Volume
        df = hist.copy()
        # Ensure capitalization matches what mpf expects
        df.columns = [c.capitalize() for c in df.columns]
        
        # Add moving averages plots
        add_plots = []
        if sma_50_col in hist.columns and not hist[sma_50_col].isnull().all():
             add_plots.append(mpf.make_addplot(hist[sma_50_col], color='orange', width=1.5))
        if sma_200_col in hist.columns and not hist[sma_200_col].isnull().all():
             add_plots.append(mpf.make_addplot(hist[sma_200_col], color='blue', width=1.5))
        
        # Create temp file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{ticker}_{timestamp}_chart.png"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
        # Plot
        # style='yahoo' gives a familiar look
        # volume=True adds volume bars
        mpf.plot(
            df, 
            type='candle', 
            style='yahoo', 
            volume=True, 
            addplot=add_plots, 
            savefig=filepath,
            title=f"{ticker} Price & Volume",
            tight_layout=True
        )
        return filepath
    except ImportError:
        return "Error: mplfinance not installed"
    except Exception as e:
        return f"Error generating chart: {str(e)}"

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

def get_stock_data(ticker, period="1mo", interval="1d"):
    """
    Fetches stock data using yfinance.
    Returns symbol, fundamentals, technicals, news (with sentiment), history, and chat path.
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

        # Slice for output/charting
        if period != "max":
            if period == '5d':   output_hist = hist.tail(5)
            elif period == '1mo': output_hist = hist.tail(22)
            elif period == '3mo': output_hist = hist.tail(66)
            elif period == '6mo': output_hist = hist.tail(132)
            elif period == '1y':  output_hist = hist.tail(252)
            elif period == '2y':  output_hist = hist.tail(504)
            elif period == '5y':  output_hist = hist.tail(1260)
            else: output_hist = hist.tail(22) # fallback for 1mo or unknown
        else:
            output_hist = hist

        # Generate Chart
        # We use the sliced history for the chart for relevance
        chart_path = generate_chart_image(ticker, output_hist, 'SMA_50', 'SMA_200')

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

        # 3. Financials
        fin_data = {}
        try:
             financials = stock.financials
             if financials is not None and not financials.empty:
                 latest_date = financials.columns[0]
                 fin_data = {
                     "reportDate": latest_date.strftime('%Y-%m-%d'),
                     "totalRevenue": int(financials.loc['Total Revenue'].iloc[0]) if 'Total Revenue' in financials.index else None,
                     "netIncome": int(financials.loc['Net Income'].iloc[0]) if 'Net Income' in financials.index else None,
                 }
        except Exception:
            pass

        # 4. News with Sentiment
        news_list = []
        sentiment_scores = []
        try:
            raw_news = stock.news
            for item in raw_news[:5]:
                content = item.get('content', item)
                title = content.get('title')
                pub_date = content.get('pubDate') or content.get('providerPublishTime')
                
                link = content.get('link')
                if not link:
                    ctu = content.get('clickThroughUrl')
                    if ctu: link = ctu.get('url')
                
                publisher = content.get('publisher')
                if not publisher:
                    prov = content.get('provider')
                    if prov: publisher = prov.get('displayName')
                
                # Sentiment Analysis
                polarity, subjectivity = analyze_sentiment(title)
                if polarity is not None:
                     sentiment_scores.append(polarity)

                news_list.append({
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "providerPublishTime": str(pub_date) if pub_date else None,
                    "sentiment": {
                        "polarity": round(polarity, 2) if polarity is not None else None,
                        "subjectivity": round(subjectivity, 2) if subjectivity is not None else None
                    }
                })
        except Exception:
            pass
            
        avg_sentiment = 0
        if sentiment_scores:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        return {
            "symbol": ticker.upper(),
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "fundamentals": fundamentals,
            "financials": fin_data,
            "technicals": technicals,
            "chart": chart_path,
            "news_sentiment": {
                "average_polarity": round(avg_sentiment, 2),
                "note": "Polarity ranges from -1 (Negative) to 1 (Positive)"
            },
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
