"""Multi-source data fetching with caching and fallback logic."""

import json
import urllib.request
from datetime import datetime
from typing import Dict, Any, Optional, Union
import pandas as pd

from .cache import DataCache
from .market_handler import MarketHandler


class DataFetcher:
    """
    Fetches stock data from multiple sources with fallback logic.

    Data source priority:
    1. Cache (if available and not expired)
    2. yfinance library (primary)
    3. Raw Yahoo Finance API (fallback)
    4. Error (no mock data in production)
    """

    def __init__(self, cache_dir: str = './data/cache', cache_ttl: int = 15):
        """
        Initialize the data fetcher.

        Args:
            cache_dir: Directory for cache storage
            cache_ttl: Cache time-to-live in minutes
        """
        self.cache = DataCache(cache_dir=cache_dir, ttl_minutes=cache_ttl)
        self.market_handler = MarketHandler()

    def fetch_stock_data(self, ticker: str, period: str = '1mo', interval: str = '1d') -> Dict[str, Any]:
        """
        Fetch stock data with multi-level fallback.

        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max)
            interval: Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)

        Returns:
            Dictionary with stock data and metadata

        Raises:
            Exception if all data sources fail
        """
        ticker = self.market_handler.normalize_ticker(ticker)

        # Level 1: Try cache
        cache_key = f"{ticker}_{period}_{interval}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            cached_data['metadata']['cached'] = True
            return cached_data

        # Level 2: Try yfinance
        try:
            data = self._fetch_with_yfinance(ticker, period, interval)
            data['metadata']['cached'] = False
            data['metadata']['source'] = 'yfinance'
            self.cache.set(cache_key, data)
            return data
        except Exception as e:
            error_msg = str(e)
            # Try fallback if yfinance fails

        # Level 3: Try raw Yahoo Finance API
        try:
            data = self._fetch_with_raw_api(ticker, period)
            data['metadata']['cached'] = False
            data['metadata']['source'] = 'yahoo_api'
            self.cache.set(cache_key, data)
            return data
        except Exception as fallback_e:
            # All sources failed
            return {
                'metadata': {
                    'ticker': ticker,
                    'timestamp': datetime.now().isoformat(),
                    'error': True
                },
                'error': {
                    'message': f'Unable to fetch data for {ticker}',
                    'code': 'DATA_FETCH_FAILED',
                    'details': f'yfinance: {error_msg}, yahoo_api: {str(fallback_e)}',
                    'source': 'all_sources_failed'
                }
            }

    def _fetch_with_yfinance(self, ticker: str, period: str, interval: str) -> Dict[str, Any]:
        """
        Fetch data using yfinance library.

        Args:
            ticker: Stock ticker symbol
            period: Time period
            interval: Data interval

        Returns:
            Dictionary with stock data

        Raises:
            Exception if yfinance fails
        """
        try:
            import yfinance as yf
        except ImportError:
            raise Exception("yfinance not installed")
        except Exception as e:
            raise Exception(f"yfinance import error: {str(e)}")

        stock = yf.Ticker(ticker)

        # Get historical data
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            raise Exception(f"No data returned for {ticker}")

        # Get current info
        info = stock.info

        # Extract market configuration
        market_config = self.market_handler.get_market_config(ticker)

        # Prepare response
        current_price = info.get('regularMarketPrice') or info.get('currentPrice')
        if current_price is None and not hist.empty:
            current_price = float(hist['Close'].iloc[-1])

        # Prepare historical data
        history = []
        for date, row in hist.iterrows():
            history.append({
                'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
                'open': round(float(row['Open']), 2) if pd.notna(row['Open']) else None,
                'high': round(float(row['High']), 2) if pd.notna(row['High']) else None,
                'low': round(float(row['Low']), 2) if pd.notna(row['Low']) else None,
                'close': round(float(row['Close']), 2) if pd.notna(row['Close']) else None,
                'volume': int(row['Volume']) if pd.notna(row['Volume']) else None
            })

        return {
            'metadata': {
                'ticker': ticker,
                'market': self.market_handler.detect_market(ticker),
                'timestamp': datetime.now().isoformat(),
                'currency': market_config['currency'],
                'period': period,
                'interval': interval
            },
            'price': {
                'current': round(current_price, 2) if current_price else None,
                'open': round(float(hist['Open'].iloc[-1]), 2) if not hist.empty and pd.notna(hist['Open'].iloc[-1]) else None,
                'high': round(float(hist['High'].iloc[-1]), 2) if not hist.empty and pd.notna(hist['High'].iloc[-1]) else None,
                'low': round(float(hist['Low'].iloc[-1]), 2) if not hist.empty and pd.notna(hist['Low'].iloc[-1]) else None,
                'volume': int(hist['Volume'].iloc[-1]) if not hist.empty and pd.notna(hist['Volume'].iloc[-1]) else None,
                'change': None,  # Calculate if previous close available
                'change_pct': None
            },
            'history': history,
            'dataframe': hist  # Keep for technical analysis
        }

    def _fetch_with_raw_api(self, ticker: str, period: str = '1mo') -> Dict[str, Any]:
        """
        Fetch data using raw Yahoo Finance API.

        Args:
            ticker: Stock ticker symbol
            period: Time period (1mo default)

        Returns:
            Dictionary with stock data

        Raises:
            Exception if API call fails
        """
        # Map period to range parameter
        range_map = {
            '1d': '1d',
            '5d': '5d',
            '1mo': '1mo',
            '3mo': '3mo',
            '6mo': '6mo',
            '1y': '1y',
            '5y': '5y',
            'max': 'max'
        }
        range_param = range_map.get(period, '1mo')

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range={range_param}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        result = data.get('chart', {}).get('result', [])[0]
        meta = result.get('meta', {})
        timestamps = result.get('timestamp', [])
        indicators = result.get('indicators', {}).get('quote', [{}])[0]

        # Extract market configuration
        market_config = self.market_handler.get_market_config(ticker)

        # Prepare historical data
        history = []
        closes = indicators.get('close', [])
        opens = indicators.get('open', [])
        highs = indicators.get('high', [])
        lows = indicators.get('low', [])
        volumes = indicators.get('volume', [])

        for i in range(len(timestamps)):
            if closes[i] is not None:
                history.append({
                    'date': datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d'),
                    'open': round(opens[i], 2) if opens[i] else None,
                    'high': round(highs[i], 2) if highs[i] else None,
                    'low': round(lows[i], 2) if lows[i] else None,
                    'close': round(closes[i], 2),
                    'volume': volumes[i] if volumes[i] else None
                })

        current_price = meta.get('regularMarketPrice')

        return {
            'metadata': {
                'ticker': meta.get('symbol', ticker),
                'market': self.market_handler.detect_market(ticker),
                'timestamp': datetime.now().isoformat(),
                'currency': market_config['currency'],
                'period': period,
                'interval': '1d'
            },
            'price': {
                'current': round(current_price, 2) if current_price else None,
                'open': history[-1]['open'] if history else None,
                'high': history[-1]['high'] if history else None,
                'low': history[-1]['low'] if history else None,
                'volume': history[-1]['volume'] if history else None,
                'change': None,
                'change_pct': None
            },
            'history': history
        }

    def get_dataframe(self, ticker: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """
        Get historical data as pandas DataFrame for technical analysis.

        Args:
            ticker: Stock ticker symbol
            period: Time period

        Returns:
            DataFrame with OHLCV data, or None if fetch fails
        """
        data = self.fetch_stock_data(ticker, period)

        if 'error' in data:
            return None

        # If yfinance was used, return the dataframe directly
        if 'dataframe' in data:
            return data['dataframe']

        # Otherwise, convert history to dataframe
        if 'history' in data and data['history']:
            df = pd.DataFrame(data['history'])
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
            return df

        return None
