"""Technical indicator calculations using pandas-ta."""

import pandas as pd
from typing import Dict, Any, Optional


class TechnicalIndicators:
    """
    Calculate technical indicators using pandas-ta library.

    Supports 15+ indicators across different categories:
    - Trend: SMA, EMA, MACD, ADX
    - Momentum: RSI, Stochastic, CCI, ROC
    - Volatility: Bollinger Bands, ATR, Standard Deviation
    - Volume: OBV, VWAP
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize with OHLCV DataFrame.

        Args:
            df: DataFrame with columns [Open, High, Low, Close, Volume]
        """
        self.df = df.copy()

        # Import pandas_ta and add to DataFrame
        try:
            import pandas_ta as ta
            self.df.ta.core()  # Initialize pandas_ta
            self.ta = ta
        except ImportError:
            raise ImportError("pandas-ta not installed. Please run: pip install pandas-ta")

    def calculate_all(self) -> Dict[str, Any]:
        """
        Calculate all technical indicators and return as dictionary.

        Returns:
            Dictionary with all calculated indicators
        """
        if len(self.df) < 200:
            # Not enough data for 200-day SMA, but we can calculate others
            pass

        indicators = {}

        # Trend Indicators
        indicators.update(self._calculate_trend())

        # Momentum Indicators
        indicators.update(self._calculate_momentum())

        # Volatility Indicators
        indicators.update(self._calculate_volatility())

        # Volume Indicators
        indicators.update(self._calculate_volume())

        return indicators

    def _calculate_trend(self) -> Dict[str, Any]:
        """Calculate trend indicators."""
        trend = {}

        # Simple Moving Averages
        sma_20 = self.df.ta.sma(length=20)
        sma_50 = self.df.ta.sma(length=50)
        sma_200 = self.df.ta.sma(length=200) if len(self.df) >= 200 else None

        trend['sma_20'] = round(float(sma_20.iloc[-1]), 2) if not sma_20.empty and pd.notna(sma_20.iloc[-1]) else None
        trend['sma_50'] = round(float(sma_50.iloc[-1]), 2) if not sma_50.empty and pd.notna(sma_50.iloc[-1]) else None
        trend['sma_200'] = round(float(sma_200.iloc[-1]), 2) if sma_200 is not None and not sma_200.empty and pd.notna(sma_200.iloc[-1]) else None

        # Exponential Moving Averages
        ema_12 = self.df.ta.ema(length=12)
        ema_26 = self.df.ta.ema(length=26)

        trend['ema_12'] = round(float(ema_12.iloc[-1]), 2) if not ema_12.empty and pd.notna(ema_12.iloc[-1]) else None
        trend['ema_26'] = round(float(ema_26.iloc[-1]), 2) if not ema_26.empty and pd.notna(ema_26.iloc[-1]) else None

        # MACD
        macd_result = self.df.ta.macd()
        if macd_result is not None and not macd_result.empty:
            trend['macd'] = {
                'macd': round(float(macd_result[f'MACD_12_26_9'].iloc[-1]), 4) if pd.notna(macd_result[f'MACD_12_26_9'].iloc[-1]) else None,
                'signal': round(float(macd_result[f'MACDs_12_26_9'].iloc[-1]), 4) if pd.notna(macd_result[f'MACDs_12_26_9'].iloc[-1]) else None,
                'histogram': round(float(macd_result[f'MACDh_12_26_9'].iloc[-1]), 4) if pd.notna(macd_result[f'MACDh_12_26_9'].iloc[-1]) else None
            }
        else:
            trend['macd'] = {'macd': None, 'signal': None, 'histogram': None}

        # ADX (Average Directional Index)
        adx_result = self.df.ta.adx(length=14)
        if adx_result is not None and not adx_result.empty:
            trend['adx'] = round(float(adx_result['ADX_14'].iloc[-1]), 2) if pd.notna(adx_result['ADX_14'].iloc[-1]) else None
        else:
            trend['adx'] = None

        return trend

    def _calculate_momentum(self) -> Dict[str, Any]:
        """Calculate momentum indicators."""
        momentum = {}

        # RSI (Relative Strength Index)
        rsi = self.df.ta.rsi(length=14)
        momentum['rsi_14'] = round(float(rsi.iloc[-1]), 2) if not rsi.empty and pd.notna(rsi.iloc[-1]) else None

        # Stochastic Oscillator
        stoch_result = self.df.ta.stoch()
        if stoch_result is not None and not stoch_result.empty:
            momentum['stoch_k'] = round(float(stoch_result['STOCHk_14_3_3'].iloc[-1]), 2) if pd.notna(stoch_result['STOCHk_14_3_3'].iloc[-1]) else None
            momentum['stoch_d'] = round(float(stoch_result['STOCHd_14_3_3'].iloc[-1]), 2) if pd.notna(stoch_result['STOCHd_14_3_3'].iloc[-1]) else None
        else:
            momentum['stoch_k'] = None
            momentum['stoch_d'] = None

        # CCI (Commodity Channel Index)
        cci = self.df.ta.cci(length=20)
        momentum['cci'] = round(float(cci.iloc[-1]), 2) if not cci.empty and pd.notna(cci.iloc[-1]) else None

        # ROC (Rate of Change)
        roc = self.df.ta.roc(length=12)
        momentum['roc'] = round(float(roc.iloc[-1]), 2) if not roc.empty and pd.notna(roc.iloc[-1]) else None

        return momentum

    def _calculate_volatility(self) -> Dict[str, Any]:
        """Calculate volatility indicators."""
        volatility = {}

        # Bollinger Bands
        bb_result = self.df.ta.bbands(length=20, std=2)
        if bb_result is not None and not bb_result.empty:
            volatility['bb_upper'] = round(float(bb_result['BBU_20_2.0'].iloc[-1]), 2) if pd.notna(bb_result['BBU_20_2.0'].iloc[-1]) else None
            volatility['bb_middle'] = round(float(bb_result['BBM_20_2.0'].iloc[-1]), 2) if pd.notna(bb_result['BBM_20_2.0'].iloc[-1]) else None
            volatility['bb_lower'] = round(float(bb_result['BBL_20_2.0'].iloc[-1]), 2) if pd.notna(bb_result['BBL_20_2.0'].iloc[-1]) else None
            volatility['bb_bandwidth'] = round(float(bb_result['BBB_20_2.0'].iloc[-1]), 4) if pd.notna(bb_result['BBB_20_2.0'].iloc[-1]) else None
        else:
            volatility['bb_upper'] = None
            volatility['bb_middle'] = None
            volatility['bb_lower'] = None
            volatility['bb_bandwidth'] = None

        # ATR (Average True Range)
        atr = self.df.ta.atr(length=14)
        volatility['atr'] = round(float(atr.iloc[-1]), 2) if not atr.empty and pd.notna(atr.iloc[-1]) else None

        # Standard Deviation
        stdev = self.df.ta.stdev(length=20)
        volatility['stdev'] = round(float(stdev.iloc[-1]), 4) if not stdev.empty and pd.notna(stdev.iloc[-1]) else None

        return volatility

    def _calculate_volume(self) -> Dict[str, Any]:
        """Calculate volume indicators."""
        volume = {}

        # OBV (On-Balance Volume)
        obv = self.df.ta.obv()
        volume['obv'] = int(obv.iloc[-1]) if not obv.empty and pd.notna(obv.iloc[-1]) else None

        # VWAP (Volume Weighted Average Price)
        # VWAP requires intraday data, skip if daily data
        try:
            vwap = self.df.ta.vwap()
            volume['vwap'] = round(float(vwap.iloc[-1]), 2) if vwap is not None and not vwap.empty and pd.notna(vwap.iloc[-1]) else None
        except:
            volume['vwap'] = None

        return volume

    def get_current_price(self) -> float:
        """Get the most recent close price."""
        return round(float(self.df['Close'].iloc[-1]), 2)

    def get_price_change(self, days: int = 1) -> Dict[str, float]:
        """
        Calculate price change over specified days.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with change and change_pct
        """
        if len(self.df) < days + 1:
            return {'change': None, 'change_pct': None}

        current = self.df['Close'].iloc[-1]
        previous = self.df['Close'].iloc[-(days + 1)]

        change = current - previous
        change_pct = (change / previous) * 100 if previous != 0 else 0

        return {
            'change': round(float(change), 2),
            'change_pct': round(float(change_pct), 2)
        }
