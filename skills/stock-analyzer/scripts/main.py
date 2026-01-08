#!/usr/bin/env python3
"""
Stock Analyzer CLI - Main entry point.

Usage:
    python3 main.py --ticker AAPL
    python3 main.py --ticker AAPL --technical
    python3 main.py --ticker 0700.HK --technical
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.data_fetcher import DataFetcher
from core.market_handler import MarketHandler
from technical.indicators import TechnicalIndicators
from technical.signals import SignalGenerator
from utils.formatters import JSONFormatter
from utils.validators import InputValidator


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Stock Analyzer - Financial stock analysis tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ticker AAPL
  %(prog)s --ticker AAPL --technical
  %(prog)s --ticker 0700.HK --technical
  %(prog)s --ticker 600519.SS --technical
  %(prog)s --ticker AAPL --period 3mo
        """
    )

    parser.add_argument(
        '--ticker',
        type=str,
        required=True,
        help='Stock ticker symbol (e.g., AAPL, 0700.HK, 600519.SS)'
    )

    parser.add_argument(
        '--technical',
        action='store_true',
        help='Include technical analysis (indicators and signals)'
    )

    parser.add_argument(
        '--period',
        type=str,
        default='1mo',
        choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
        help='Time period for historical data (default: 1mo)'
    )

    parser.add_argument(
        '--interval',
        type=str,
        default='1d',
        choices=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'],
        help='Data interval (default: 1d)'
    )

    parser.add_argument(
        '--cache-dir',
        type=str,
        default='./data/cache',
        help='Cache directory path (default: ./data/cache)'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching (always fetch fresh data)'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    # Validate ticker
    is_valid, error_msg = InputValidator.validate_ticker(args.ticker)
    if not is_valid:
        print(JSONFormatter.format_error(args.ticker, error_msg))
        sys.exit(1)

    try:
        # Initialize data fetcher
        cache_ttl = 0 if args.no_cache else 15
        fetcher = DataFetcher(cache_dir=args.cache_dir, cache_ttl=cache_ttl)

        # Fetch stock data
        data = fetcher.fetch_stock_data(
            ticker=args.ticker,
            period=args.period,
            interval=args.interval
        )

        # Check for errors
        if 'error' in data:
            print(JSONFormatter.format_simple(data))
            sys.exit(1)

        # Technical analysis
        indicators = None
        signals = None

        if args.technical:
            # Get dataframe for technical analysis
            df = fetcher.get_dataframe(args.ticker, args.period)

            if df is not None and not df.empty:
                try:
                    # Calculate indicators
                    tech_analyzer = TechnicalIndicators(df)
                    indicators = tech_analyzer.calculate_all()

                    # Generate signals
                    signals = SignalGenerator.generate_signals(indicators, df)

                    # Add price change
                    price_change = tech_analyzer.get_price_change(days=1)
                    if data.get('price'):
                        data['price']['change'] = price_change.get('change')
                        data['price']['change_pct'] = price_change.get('change_pct')

                except Exception as e:
                    # Technical analysis failed, but we still have price data
                    print(JSONFormatter.format_simple({
                        **data,
                        'warning': f'Technical analysis failed: {str(e)}'
                    }))
                    sys.exit(0)

        # Format and output
        output = JSONFormatter.format_stock_analysis(data, indicators, signals)
        print(output)

    except KeyboardInterrupt:
        print('\n\nInterrupted by user', file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(JSONFormatter.format_error(
            args.ticker,
            f'Unexpected error: {str(e)}',
            details=str(type(e).__name__)
        ))
        sys.exit(1)


if __name__ == '__main__':
    main()
