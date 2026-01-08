"""Input validation utilities."""

import re
from typing import Tuple, Optional


class InputValidator:
    """
    Validate user inputs for stock tickers and parameters.
    """

    @staticmethod
    def validate_ticker(ticker: str) -> Tuple[bool, Optional[str]]:
        """
        Validate stock ticker format.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not ticker:
            return False, "Ticker cannot be empty"

        if len(ticker) > 10:
            return False, "Ticker too long (max 10 characters)"

        # Allow alphanumeric, dots, and hyphens
        if not re.match(r'^[A-Za-z0-9.\-]+$', ticker):
            return False, "Ticker contains invalid characters"

        return True, None

    @staticmethod
    def validate_period(period: str) -> Tuple[bool, Optional[str]]:
        """
        Validate time period parameter.

        Args:
            period: Time period string

        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

        if period not in valid_periods:
            return False, f"Invalid period. Must be one of: {', '.join(valid_periods)}"

        return True, None

    @staticmethod
    def validate_interval(interval: str) -> Tuple[bool, Optional[str]]:
        """
        Validate data interval parameter.

        Args:
            interval: Data interval string

        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

        if interval not in valid_intervals:
            return False, f"Invalid interval. Must be one of: {', '.join(valid_intervals)}"

        return True, None
