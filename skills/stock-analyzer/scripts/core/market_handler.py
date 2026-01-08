"""Market detection and configuration for different stock exchanges."""

from typing import Dict, Any


class MarketHandler:
    """
    Handles market-specific logic for different stock exchanges.

    Supports:
    - US stocks (NYSE, NASDAQ)
    - Hong Kong stocks (.HK)
    - China A-shares (Shanghai .SS, Shenzhen .SZ)
    - Cryptocurrencies (-USD)
    """

    MARKET_CONFIGS = {
        'us': {
            'name': 'US Market',
            'timezone': 'America/New_York',
            'currency': 'USD',
            'trading_hours': '09:30-16:00',
            'suffixes': []
        },
        'hong_kong': {
            'name': 'Hong Kong Stock Exchange',
            'timezone': 'Asia/Hong_Kong',
            'currency': 'HKD',
            'trading_hours': '09:30-16:00',
            'suffixes': ['.HK']
        },
        'china_a_shares': {
            'name': 'China A-Shares',
            'timezone': 'Asia/Shanghai',
            'currency': 'CNY',
            'trading_hours': '09:30-15:00',
            'suffixes': ['.SS', '.SZ']  # Shanghai, Shenzhen
        },
        'crypto': {
            'name': 'Cryptocurrency',
            'timezone': 'UTC',
            'currency': 'USD',
            'trading_hours': '24/7',
            'suffixes': ['-USD', '-BTC', '-ETH']
        }
    }

    @classmethod
    def detect_market(cls, ticker: str) -> str:
        """
        Auto-detect market from ticker format.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Market identifier: 'us', 'hong_kong', 'china_a_shares', or 'crypto'

        Examples:
            >>> MarketHandler.detect_market('AAPL')
            'us'
            >>> MarketHandler.detect_market('0700.HK')
            'hong_kong'
            >>> MarketHandler.detect_market('600519.SS')
            'china_a_shares'
            >>> MarketHandler.detect_market('BTC-USD')
            'crypto'
        """
        ticker_upper = ticker.upper()

        # Check Hong Kong
        if ticker_upper.endswith('.HK'):
            return 'hong_kong'

        # Check China A-shares
        if ticker_upper.endswith('.SS') or ticker_upper.endswith('.SZ'):
            return 'china_a_shares'

        # Check Crypto
        if any(suffix in ticker_upper for suffix in ['-USD', '-BTC', '-ETH']):
            return 'crypto'

        # Default to US market
        return 'us'

    @classmethod
    def get_market_config(cls, ticker: str) -> Dict[str, Any]:
        """
        Get market-specific configuration for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with market configuration (name, timezone, currency, etc.)
        """
        market = cls.detect_market(ticker)
        return cls.MARKET_CONFIGS.get(market, cls.MARKET_CONFIGS['us'])

    @classmethod
    def get_currency(cls, ticker: str) -> str:
        """
        Get the currency for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Currency code (USD, HKD, CNY, etc.)
        """
        config = cls.get_market_config(ticker)
        return config['currency']

    @classmethod
    def get_timezone(cls, ticker: str) -> str:
        """
        Get the timezone for a ticker's market.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Timezone string (e.g., 'America/New_York')
        """
        config = cls.get_market_config(ticker)
        return config['timezone']

    @classmethod
    def normalize_ticker(cls, ticker: str) -> str:
        """
        Normalize ticker symbol (uppercase, strip whitespace).

        Args:
            ticker: Stock ticker symbol

        Returns:
            Normalized ticker
        """
        return ticker.upper().strip()

    @classmethod
    def is_chinese_market(cls, ticker: str) -> bool:
        """
        Check if ticker is from Chinese markets (HK or A-shares).

        Args:
            ticker: Stock ticker symbol

        Returns:
            True if ticker is from HK or China A-shares
        """
        market = cls.detect_market(ticker)
        return market in ['hong_kong', 'china_a_shares']
