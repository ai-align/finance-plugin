"""Trading signal generation from technical indicators."""

from typing import Dict, Any
import pandas as pd


class SignalGenerator:
    """
    Generate trading signals based on technical indicators.

    Signals include:
    - RSI overbought/oversold
    - MACD bullish/bearish
    - Bollinger Band position
    - Trend direction
    - Overall recommendation
    """

    @staticmethod
    def generate_signals(indicators: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate trading signals from indicators.

        Args:
            indicators: Dictionary of calculated technical indicators
            df: Price DataFrame for additional analysis

        Returns:
            Dictionary with trading signals
        """
        signals = {}

        # RSI signals
        signals['rsi_signal'] = SignalGenerator._rsi_signal(indicators.get('rsi_14'))

        # MACD signals
        macd_data = indicators.get('macd', {})
        signals['macd_signal'] = SignalGenerator._macd_signal(macd_data)

        # Bollinger Bands signals
        bb_signal = SignalGenerator._bb_signal(
            df['Close'].iloc[-1] if not df.empty else None,
            indicators.get('bb_upper'),
            indicators.get('bb_middle'),
            indicators.get('bb_lower')
        )
        signals['bb_signal'] = bb_signal

        # Trend signals
        signals['trend'] = SignalGenerator._trend_signal(
            df['Close'].iloc[-1] if not df.empty else None,
            indicators.get('sma_50'),
            indicators.get('sma_200'),
            indicators.get('ema_12'),
            indicators.get('ema_26')
        )

        # Stochastic signals
        signals['stoch_signal'] = SignalGenerator._stochastic_signal(
            indicators.get('stoch_k'),
            indicators.get('stoch_d')
        )

        # Volume signal
        signals['volume_signal'] = SignalGenerator._volume_signal(df) if not df.empty else 'neutral'

        # Overall recommendation
        signals['recommendation'] = SignalGenerator._overall_recommendation(signals)

        return signals

    @staticmethod
    def _rsi_signal(rsi: float) -> str:
        """
        Generate RSI signal.

        Args:
            rsi: RSI value (0-100)

        Returns:
            Signal: 'overbought', 'oversold', 'neutral'
        """
        if rsi is None:
            return 'unknown'

        if rsi >= 70:
            return 'overbought'
        elif rsi <= 30:
            return 'oversold'
        else:
            return 'neutral'

    @staticmethod
    def _macd_signal(macd: Dict[str, float]) -> str:
        """
        Generate MACD signal.

        Args:
            macd: Dictionary with macd, signal, histogram values

        Returns:
            Signal: 'bullish', 'bearish', 'neutral'
        """
        if not macd or macd.get('histogram') is None:
            return 'unknown'

        histogram = macd['histogram']
        macd_line = macd.get('macd')
        signal_line = macd.get('signal')

        if histogram > 0:
            return 'bullish'
        elif histogram < 0:
            return 'bearish'
        else:
            return 'neutral'

    @staticmethod
    def _bb_signal(price: float, bb_upper: float, bb_middle: float, bb_lower: float) -> str:
        """
        Generate Bollinger Bands signal.

        Args:
            price: Current price
            bb_upper: Upper Bollinger Band
            bb_middle: Middle Bollinger Band
            bb_lower: Lower Bollinger Band

        Returns:
            Signal: 'overbought', 'oversold', 'normal', 'unknown'
        """
        if None in [price, bb_upper, bb_middle, bb_lower]:
            return 'unknown'

        if price >= bb_upper:
            return 'overbought'
        elif price <= bb_lower:
            return 'oversold'
        else:
            return 'normal'

    @staticmethod
    def _trend_signal(price: float, sma_50: float, sma_200: float, ema_12: float, ema_26: float) -> str:
        """
        Generate trend signal.

        Args:
            price: Current price
            sma_50: 50-day SMA
            sma_200: 200-day SMA
            ema_12: 12-day EMA
            ema_26: 26-day EMA

        Returns:
            Signal: 'strong_uptrend', 'uptrend', 'strong_downtrend', 'downtrend', 'sideways'
        """
        if price is None:
            return 'unknown'

        # Golden Cross / Death Cross (50 vs 200 SMA)
        if sma_50 is not None and sma_200 is not None:
            if price > sma_50 > sma_200:
                return 'strong_uptrend'
            elif price < sma_50 < sma_200:
                return 'strong_downtrend'

        # EMA trend
        if sma_50 is not None:
            if price > sma_50:
                return 'uptrend'
            elif price < sma_50:
                return 'downtrend'

        return 'sideways'

    @staticmethod
    def _stochastic_signal(stoch_k: float, stoch_d: float) -> str:
        """
        Generate Stochastic signal.

        Args:
            stoch_k: %K line
            stoch_d: %D line

        Returns:
            Signal: 'overbought', 'oversold', 'neutral'
        """
        if stoch_k is None or stoch_d is None:
            return 'unknown'

        if stoch_k >= 80 and stoch_d >= 80:
            return 'overbought'
        elif stoch_k <= 20 and stoch_d <= 20:
            return 'oversold'
        else:
            return 'neutral'

    @staticmethod
    def _volume_signal(df: pd.DataFrame) -> str:
        """
        Generate volume signal.

        Args:
            df: Price DataFrame with Volume column

        Returns:
            Signal: 'high', 'low', 'normal'
        """
        if 'Volume' not in df.columns or len(df) < 20:
            return 'unknown'

        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]

        if pd.isna(current_volume) or pd.isna(avg_volume) or avg_volume == 0:
            return 'unknown'

        ratio = current_volume / avg_volume

        if ratio > 1.5:
            return 'high'
        elif ratio < 0.5:
            return 'low'
        else:
            return 'normal'

    @staticmethod
    def _overall_recommendation(signals: Dict[str, str]) -> str:
        """
        Generate overall trading recommendation.

        Args:
            signals: Dictionary of all signals

        Returns:
            Recommendation: 'strong_buy', 'buy', 'hold', 'sell', 'strong_sell'
        """
        # Count bullish and bearish signals
        bullish_count = 0
        bearish_count = 0

        # RSI
        if signals.get('rsi_signal') == 'oversold':
            bullish_count += 1
        elif signals.get('rsi_signal') == 'overbought':
            bearish_count += 1

        # MACD
        if signals.get('macd_signal') == 'bullish':
            bullish_count += 1
        elif signals.get('macd_signal') == 'bearish':
            bearish_count += 1

        # Bollinger Bands
        if signals.get('bb_signal') == 'oversold':
            bullish_count += 1
        elif signals.get('bb_signal') == 'overbought':
            bearish_count += 1

        # Trend (double weight for trend)
        if signals.get('trend') in ['strong_uptrend', 'uptrend']:
            bullish_count += 2
        elif signals.get('trend') in ['strong_downtrend', 'downtrend']:
            bearish_count += 2

        # Stochastic
        if signals.get('stoch_signal') == 'oversold':
            bullish_count += 1
        elif signals.get('stoch_signal') == 'overbought':
            bearish_count += 1

        # Calculate recommendation
        total = bullish_count + bearish_count
        if total == 0:
            return 'hold'

        bullish_ratio = bullish_count / total

        if bullish_ratio >= 0.75:
            return 'strong_buy'
        elif bullish_ratio >= 0.6:
            return 'buy'
        elif bullish_ratio <= 0.25:
            return 'strong_sell'
        elif bullish_ratio <= 0.4:
            return 'sell'
        else:
            return 'hold'
