"""JSON output formatting utilities."""

from typing import Dict, Any
import json


class JSONFormatter:
    """
    Format data into standardized JSON output.

    Ensures consistent structure across all command outputs.
    """

    @staticmethod
    def format_stock_analysis(
        data: Dict[str, Any],
        indicators: Dict[str, Any] = None,
        signals: Dict[str, Any] = None
    ) -> str:
        """
        Format complete stock analysis output.

        Args:
            data: Basic stock data from DataFetcher
            indicators: Technical indicators (optional)
            signals: Trading signals (optional)

        Returns:
            Formatted JSON string
        """
        output = {
            'metadata': data.get('metadata', {}),
            'price': data.get('price', {})
        }

        # Add technical analysis if available
        if indicators and signals:
            output['technical'] = {
                'indicators': indicators,
                'signals': signals
            }

        # Add history (limit to last 10 days for output)
        if 'history' in data and data['history']:
            output['history'] = data['history'][-10:]

        return json.dumps(output, indent=2)

    @staticmethod
    def format_error(ticker: str, error_message: str, details: str = None) -> str:
        """
        Format error output.

        Args:
            ticker: Stock ticker
            error_message: Error message
            details: Additional error details

        Returns:
            Formatted JSON error string
        """
        from datetime import datetime

        error_output = {
            'metadata': {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'error': True
            },
            'error': {
                'message': error_message,
                'code': 'ERROR'
            }
        }

        if details:
            error_output['error']['details'] = details

        return json.dumps(error_output, indent=2)

    @staticmethod
    def format_simple(data: Dict[str, Any]) -> str:
        """
        Simple JSON formatting with indentation.

        Args:
            data: Dictionary to format

        Returns:
            Formatted JSON string
        """
        return json.dumps(data, indent=2, default=str)
