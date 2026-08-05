"""
Trading signal generation system with technical indicators.
Provides comprehensive technical analysis and signal generation for trading decisions.
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from src.queries import PriceQueries
import yaml
import os


class SignalType(Enum):
    """Signal types for trading decisions."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class SignalStrength(Enum):
    """Signal strength levels."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


@dataclass
class TradingSignal:
    """Trading signal data structure."""
    signal_type: SignalType
    strength: SignalStrength
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    price: float
    indicators: Dict[str, Any] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    timeframe: str = "1d"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary."""
        return {
            'signal_type': self.signal_type.value,
            'strength': self.strength.value,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'price': self.price,
            'indicators': self.indicators,
            'reasons': self.reasons,
            'timeframe': self.timeframe
        }


@dataclass
class IndicatorResult:
    """Result of indicator calculation."""
    name: str
    values: pd.Series
    parameters: Dict[str, Any] = field(default_factory=dict)
    signals: List[TradingSignal] = field(default_factory=list)


class TechnicalIndicators:
    """Technical indicator calculations."""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA).
        
        Args:
            data: Price series
            period: Number of periods for average
            
        Returns:
            SMA series
        """
        return data.rolling(window=period, min_periods=1).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA).
        
        Args:
            data: Price series
            period: Number of periods for average
            
        Returns:
            EMA series
        """
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            data: Price series
            period: Lookback period (default 14)
            
        Returns:
            RSI series (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast_period: int = 12, 
             slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Price series
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line EMA period (default 9)
            
        Returns:
            Dictionary with MACD line, signal line, and histogram
        """
        ema_fast = TechnicalIndicators.ema(data, fast_period)
        ema_slow = TechnicalIndicators.ema(data, slow_period)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal_period)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, 
                       std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: Price series
            period: Period for moving average (default 20)
            std_dev: Number of standard deviations (default 2.0)
            
        Returns:
            Dictionary with upper, middle, and lower bands
        """
        sma = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    @staticmethod
    def support_resistance(data: pd.Series, window: int = 20, 
                          num_levels: int = 3) -> Dict[str, List[float]]:
        """
        Calculate support and resistance levels using local extrema.
        
        Args:
            data: Price series
            window: Window size for finding extrema
            num_levels: Number of levels to return
            
        Returns:
            Dictionary with support and resistance levels
        """
        # Find local minima (support) and maxima (resistance)
        rolling_min = data.rolling(window, center=True).min()
        rolling_max = data.rolling(window, center=True).max()
        
        # Find where price equals rolling min/max (local extrema)
        is_local_min = (data == rolling_min) & (rolling_min.notna())
        is_local_max = (data == rolling_max) & (rolling_max.notna())
        
        local_min = data[is_local_min]
        local_max = data[is_local_max]
        
        # Get recent levels
        recent_min = local_min.tail(num_levels * 2).tolist()
        recent_max = local_max.tail(num_levels * 2).tolist()
        
        # Cluster and filter levels
        support_levels = sorted(set([round(x, 2) for x in recent_min if x > 0]))[:num_levels]
        resistance_levels = sorted(set([round(x, 2) for x in recent_max if x > 0]), reverse=True)[:num_levels]
        
        return {
            'support': support_levels if support_levels else [round(data.min(), 2)],
            'resistance': resistance_levels if resistance_levels else [round(data.max(), 2)]
        }
    
    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, 
            period: int = 14) -> Dict[str, pd.Series]:
        """
        Calculate Average Directional Index (ADX).
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: Lookback period (default 14)
            
        Returns:
            Dictionary with ADX, +DI, and -DI
        """
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate directional movements
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # Smooth the values
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).rolling(window=period).mean() / atr)
        
        # Calculate ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return {
            'adx': adx,
            'plus_di': plus_di,
            'minus_di': minus_di
        }
    
    @staticmethod
    def volume_sma(volume: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Volume Simple Moving Average.
        
        Args:
            volume: Volume series
            period: Period for average
            
        Returns:
            Volume SMA series
        """
        return volume.rolling(window=period, min_periods=1).mean()
    
    @staticmethod
    def volume_ratio(volume: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Volume Ratio (current volume / average volume).
        
        Args:
            volume: Volume series
            period: Period for average volume
            
        Returns:
            Volume ratio series
        """
        vol_sma = TechnicalIndicators.volume_sma(volume, period)
        return volume / vol_sma
    
    @staticmethod
    def on_balance_volume(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        Calculate On Balance Volume (OBV).
        
        Args:
            close: Close price series
            volume: Volume series
            
        Returns:
            OBV series
        """
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv


class SignalGenerator:
    """Generate trading signals based on technical indicators."""
    
    def __init__(self, config_path: str = "config/signals.yml"):
        """
        Initialize signal generator with configuration.
        
        Args:
            config_path: Path to signals configuration file
        """
        self.config = self._load_config(config_path)
        self.indicators = TechnicalIndicators()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load signal configuration from YAML file."""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Return default configuration
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default signal configuration."""
        return {
            'indicators': {
                'sma': {'short_period': 20, 'long_period': 50},
                'ema': {'short_period': 12, 'long_period': 26},
                'rsi': {'period': 14, 'oversold': 30, 'overbought': 70},
                'macd': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
                'bollinger_bands': {'period': 20, 'std_dev': 2.0},
                'adx': {'period': 14, 'threshold': 25},
                'volume': {'period': 20, 'high_ratio': 1.5}
            },
            'signal_rules': {
                'buy_conditions': {
                    'rsi_oversold': True,
                    'macd_crossover': True,
                    'price_above_sma': True,
                    'volume_confirmation': True
                },
                'sell_conditions': {
                    'rsi_overbought': True,
                    'macd_crossover': True,
                    'price_below_sma': True,
                    'volume_confirmation': True
                },
                'min_confidence': 0.6,
                'strength_thresholds': {
                    'weak': 0.6,
                    'moderate': 0.75,
                    'strong': 0.85
                }
            },
            'timeframes': ['1d', '1w', '1m'],
            'default_timeframe': '1d'
        }
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all technical indicators for the given data.
        
        Args:
            df: DataFrame with OHLCV data (open, high, low, close, volume)
            
        Returns:
            Dictionary with all calculated indicators
        """
        if df.empty:
            return {}
        
        # Use close price for most indicators
        close = df['close'] if 'close' in df.columns else df['rate'] if 'rate' in df.columns else df['price']
        high = df['high'] if 'high' in df.columns else close
        low = df['low'] if 'low' in df.columns else close
        volume = df['volume'] if 'volume' in df.columns else pd.Series([1] * len(df), index=df.index)
        
        indicators = {}
        cfg = self.config['indicators']
        
        # Moving Averages
        indicators['sma_short'] = self.indicators.sma(close, cfg['sma']['short_period'])
        indicators['sma_long'] = self.indicators.sma(close, cfg['sma']['long_period'])
        indicators['ema_short'] = self.indicators.ema(close, cfg['ema']['short_period'])
        indicators['ema_long'] = self.indicators.ema(close, cfg['ema']['long_period'])
        
        # RSI
        indicators['rsi'] = self.indicators.rsi(close, cfg['rsi']['period'])
        
        # MACD
        macd_result = self.indicators.macd(
            close, 
            cfg['macd']['fast_period'],
            cfg['macd']['slow_period'],
            cfg['macd']['signal_period']
        )
        indicators['macd'] = macd_result['macd']
        indicators['macd_signal'] = macd_result['signal']
        indicators['macd_histogram'] = macd_result['histogram']
        
        # Bollinger Bands
        bb_result = self.indicators.bollinger_bands(
            close,
            cfg['bollinger_bands']['period'],
            cfg['bollinger_bands']['std_dev']
        )
        indicators['bb_upper'] = bb_result['upper']
        indicators['bb_middle'] = bb_result['middle']
        indicators['bb_lower'] = bb_result['lower']
        
        # Support/Resistance
        sr_result = self.indicators.support_resistance(close)
        indicators['support'] = sr_result['support']
        indicators['resistance'] = sr_result['resistance']
        
        # ADX
        adx_result = self.indicators.adx(high, low, close, cfg['adx']['period'])
        indicators['adx'] = adx_result['adx']
        indicators['plus_di'] = adx_result['plus_di']
        indicators['minus_di'] = adx_result['minus_di']
        
        # Volume indicators
        indicators['volume_sma'] = self.indicators.volume_sma(volume, cfg['volume']['period'])
        indicators['volume_ratio'] = self.indicators.volume_ratio(volume, cfg['volume']['period'])
        indicators['obv'] = self.indicators.on_balance_volume(close, volume)
        
        return indicators
    
    def generate_signal(self, df: pd.DataFrame, 
                       timeframe: str = "1d") -> TradingSignal:
        """
        Generate a trading signal based on technical indicators.
        
        Args:
            df: DataFrame with OHLCV data
            timeframe: Timeframe for analysis
            
        Returns:
            TradingSignal object
        """
        if df.empty or len(df) < 50:
            return TradingSignal(
                signal_type=SignalType.HOLD,
                strength=SignalStrength.WEAK,
                confidence=0.0,
                timestamp=datetime.now(),
                price=0.0,
                timeframe=timeframe,
                reasons=["Insufficient data for signal generation"]
            )
        
        # Calculate indicators
        indicators = self.calculate_all_indicators(df)
        
        # Get current values
        close = df['close'].iloc[-1] if 'close' in df.columns else df['rate'].iloc[-1] if 'rate' in df.columns else df['price'].iloc[-1]
        current_rsi = indicators['rsi'].iloc[-1]
        current_macd = indicators['macd'].iloc[-1]
        current_macd_signal = indicators['macd_signal'].iloc[-1]
        current_macd_hist = indicators['macd_histogram'].iloc[-1]
        current_adx = indicators['adx'].iloc[-1]
        current_plus_di = indicators['plus_di'].iloc[-1]
        current_minus_di = indicators['minus_di'].iloc[-1]
        current_vol_ratio = indicators['volume_ratio'].iloc[-1]
        
        sma_short = indicators['sma_short'].iloc[-1]
        sma_long = indicators['sma_long'].iloc[-1]
        bb_upper = indicators['bb_upper'].iloc[-1]
        bb_lower = indicators['bb_lower'].iloc[-1]
        
        cfg = self.config['indicators']
        rules = self.config['signal_rules']
        
        # Initialize signal analysis
        buy_score = 0
        sell_score = 0
        reasons = []
        
        # RSI Analysis
        if current_rsi < cfg['rsi']['oversold']:
            buy_score += 2
            reasons.append(f"RSI oversold ({current_rsi:.2f})")
        elif current_rsi > cfg['rsi']['overbought']:
            sell_score += 2
            reasons.append(f"RSI overbought ({current_rsi:.2f})")
        
        # MACD Analysis
        if current_macd > current_macd_signal and current_macd_hist > 0:
            buy_score += 2
            reasons.append("MACD bullish crossover")
        elif current_macd < current_macd_signal and current_macd_hist < 0:
            sell_score += 2
            reasons.append("MACD bearish crossover")
        
        # Moving Average Analysis
        if close > sma_short and sma_short > sma_long:
            buy_score += 1
            reasons.append("Price above short MA, short above long MA")
        elif close < sma_short and sma_short < sma_long:
            sell_score += 1
            reasons.append("Price below short MA, short below long MA")
        
        # Bollinger Bands Analysis
        if close < bb_lower:
            buy_score += 1
            reasons.append("Price below lower Bollinger Band")
        elif close > bb_upper:
            sell_score += 1
            reasons.append("Price above upper Bollinger Band")
        
        # ADX Analysis (trend strength)
        if current_adx > cfg['adx']['threshold']:
            if current_plus_di > current_minus_di:
                buy_score += 1
                reasons.append(f"Strong uptrend (ADX: {current_adx:.2f})")
            else:
                sell_score += 1
                reasons.append(f"Strong downtrend (ADX: {current_adx:.2f})")
        
        # Volume Confirmation
        if current_vol_ratio > cfg['volume']['high_ratio']:
            if buy_score > sell_score:
                buy_score += 1
                reasons.append(f"High volume confirms buy ({current_vol_ratio:.2f}x)")
            elif sell_score > buy_score:
                sell_score += 1
                reasons.append(f"High volume confirms sell ({current_vol_ratio:.2f}x)")
        
        # Determine signal type
        total_score = buy_score + sell_score
        if total_score == 0:
            signal_type = SignalType.HOLD
            confidence = 0.0
        elif buy_score > sell_score:
            signal_type = SignalType.BUY
            confidence = min(buy_score / 8.0, 1.0)  # Normalize to 0-1
        elif sell_score > buy_score:
            signal_type = SignalType.SELL
            confidence = min(sell_score / 8.0, 1.0)
        else:
            signal_type = SignalType.HOLD
            confidence = 0.0
        
        # Apply minimum confidence threshold
        if confidence < rules['min_confidence']:
            signal_type = SignalType.HOLD
            reasons.append(f"Confidence below threshold ({confidence:.2f} < {rules['min_confidence']})")
        
        # Determine signal strength
        thresholds = rules['strength_thresholds']
        if confidence >= thresholds['strong']:
            strength = SignalStrength.STRONG
        elif confidence >= thresholds['moderate']:
            strength = SignalStrength.MODERATE
        else:
            strength = SignalStrength.WEAK
        
        # Create signal
        signal = TradingSignal(
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            timestamp=datetime.now(),
            price=close,
            indicators={
                'rsi': round(current_rsi, 2),
                'macd': round(current_macd, 4),
                'macd_signal': round(current_macd_signal, 4),
                'macd_histogram': round(current_macd_hist, 4),
                'adx': round(current_adx, 2),
                'plus_di': round(current_plus_di, 2),
                'minus_di': round(current_minus_di, 2),
                'volume_ratio': round(current_vol_ratio, 2),
                'sma_short': round(sma_short, 4),
                'sma_long': round(sma_long, 4),
                'bb_upper': round(bb_upper, 4),
                'bb_lower': round(bb_lower, 4),
                'support': indicators['support'],
                'resistance': indicators['resistance']
            },
            reasons=reasons,
            timeframe=timeframe
        )
        
        return signal
    
    def generate_signals_for_timeframes(self, df: pd.DataFrame) -> Dict[str, TradingSignal]:
        """
        Generate signals for multiple timeframes.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary mapping timeframes to signals
        """
        signals = {}
        timeframes = self.config.get('timeframes', ['1d'])
        
        for tf in timeframes:
            # Resample data for timeframe
            if tf == '1d':
                resampled_df = df
            elif tf == '1w':
                resampled_df = df.resample('W').agg({
                    'open': 'first', 'high': 'max', 'low': 'min',
                    'close': 'last', 'volume': 'sum'
                }).dropna()
            elif tf == '1m':
                resampled_df = df.resample('M').agg({
                    'open': 'first', 'high': 'max', 'low': 'min',
                    'close': 'last', 'volume': 'sum'
                }).dropna()
            else:
                resampled_df = df
            
            signals[tf] = self.generate_signal(resampled_df, tf)
        
        return signals
    
    def validate_signal(self, signal: TradingSignal) -> Dict[str, Any]:
        """
        Validate signal quality and consistency.
        
        Args:
            signal: TradingSignal to validate
            
        Returns:
            Validation result dictionary
        """
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check confidence
        if signal.confidence < self.config['signal_rules']['min_confidence']:
            validation['warnings'].append(
                f"Low confidence: {signal.confidence:.2f}"
            )
        
        # Check for conflicting indicators
        if signal.signal_type == SignalType.BUY:
            if signal.indicators.get('rsi', 50) > 70:
                validation['warnings'].append(
                    "BUY signal with overbought RSI"
                )
        elif signal.signal_type == SignalType.SELL:
            if signal.indicators.get('rsi', 50) < 30:
                validation['warnings'].append(
                    "SELL signal with oversold RSI"
                )
        
        # Check ADX for trend strength
        if signal.indicators.get('adx', 0) < 20:
            validation['warnings'].append(
                "Weak trend (ADX < 20), signals may be less reliable"
            )
        
        # Check if signal is HOLD
        if signal.signal_type == SignalType.HOLD and signal.confidence > 0:
            validation['warnings'].append(
                "HOLD signal with non-zero confidence"
            )
        
        # Determine overall validity
        if len(validation['errors']) > 0:
            validation['is_valid'] = False
        
        return validation


class SignalHistory:
    """Track and manage signal history."""
    
    def __init__(self, session: Session):
        """
        Initialize signal history tracker.
        
        Args:
            session: Database session
        """
        self.session = session
    
    def save_signal(self, signal: TradingSignal, 
                   asset_type: str, 
                   asset_symbol: str) -> bool:
        """
        Save a signal to the database.
        
        Args:
            signal: TradingSignal to save
            asset_type: Type of asset (currency, commodity, dollar_index)
            asset_symbol: Symbol of the asset
            
        Returns:
            True if saved successfully
        """
        try:
            from src.models import SignalHistory as SignalHistoryModel
            
            history_entry = SignalHistoryModel(
                asset_type=asset_type,
                asset_symbol=asset_symbol,
                signal_type=signal.signal_type.value,
                strength=signal.strength.value,
                confidence=signal.confidence,
                timestamp=signal.timestamp,
                price=signal.price,
                indicators=signal.indicators,
                reasons=signal.reasons,
                timeframe=signal.timeframe
            )
            
            self.session.add(history_entry)
            self.session.commit()
            
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error saving signal: {e}")
            return False
    
    def get_recent_signals(self, asset_type: Optional[str] = None,
                          asset_symbol: Optional[str] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent signals from history.
        
        Args:
            asset_type: Filter by asset type
            asset_symbol: Filter by asset symbol
            limit: Maximum number of signals to return
            
        Returns:
            List of signal dictionaries
        """
        try:
            from src.models import SignalHistory as SignalHistoryModel
            
            query = self.session.query(SignalHistoryModel)
            
            if asset_type:
                query = query.filter(SignalHistoryModel.asset_type == asset_type)
            if asset_symbol:
                query = query.filter(SignalHistoryModel.asset_symbol == asset_symbol)
            
            signals = query.order_by(
                SignalHistoryModel.timestamp.desc()
            ).limit(limit).all()
            
            return [{
                'id': s.id,
                'asset_type': s.asset_type,
                'asset_symbol': s.asset_symbol,
                'signal_type': s.signal_type,
                'strength': s.strength,
                'confidence': s.confidence,
                'timestamp': s.timestamp.isoformat(),
                'price': s.price,
                'indicators': s.indicators,
                'reasons': s.reasons,
                'timeframe': s.timeframe
            } for s in signals]
        except Exception as e:
            print(f"Error retrieving signals: {e}")
            return []


class Backtester:
    """Backtest trading signals on historical data."""
    
    def __init__(self, signal_generator: SignalGenerator):
        """
        Initialize backtester.
        
        Args:
            signal_generator: SignalGenerator instance
        """
        self.generator = signal_generator
    
    def run_backtest(self, df: pd.DataFrame, 
                    initial_capital: float = 10000.0,
                    commission: float = 0.001) -> Dict[str, Any]:
        """
        Run backtest on historical data.
        
        Args:
            df: DataFrame with OHLCV data
            initial_capital: Starting capital
            commission: Commission per trade (as percentage)
            
        Returns:
            Backtest results dictionary
        """
        if df.empty or len(df) < 100:
            return {'error': 'Insufficient data for backtesting'}
        
        capital = initial_capital
        position = 0  # 0 = no position, 1 = long, -1 = short
        position_size = 0
        trades = []
        equity_curve = [initial_capital]
        
        # Slide through data with a window
        window_size = 50
        for i in range(window_size, len(df)):
            # Get window of data
            window_df = df.iloc[i-window_size:i]
            
            # Generate signal
            signal = self.generator.generate_signal(window_df)
            
            current_price = window_df['close'].iloc[-1] if 'close' in window_df.columns else window_df['rate'].iloc[-1]
            
            # Execute trades based on signal
            if signal.signal_type == SignalType.BUY and position <= 0:
                if position < 0:
                    # Close short position
                    pnl = position_size * (current_price - trades[-1]['entry_price'])
                    capital += pnl - abs(pnl * commission)
                
                # Open long position
                position_size = capital / current_price
                position = 1
                trades.append({
                    'type': 'BUY',
                    'entry_price': current_price,
                    'timestamp': window_df.index[-1],
                    'size': position_size
                })
                
            elif signal.signal_type == SignalType.SELL and position >= 0:
                if position > 0:
                    # Close long position
                    pnl = position_size * (current_price - trades[-1]['entry_price'])
                    capital += pnl - abs(pnl * commission)
                
                # Open short position
                position_size = capital / current_price
                position = -1
                trades.append({
                    'type': 'SELL',
                    'entry_price': current_price,
                    'timestamp': window_df.index[-1],
                    'size': position_size
                })
            
            # Calculate current equity
            if position == 1:
                current_equity = capital + position_size * (current_price - trades[-1]['entry_price'])
            elif position == -1:
                current_equity = capital + position_size * (trades[-1]['entry_price'] - current_price)
            else:
                current_equity = capital
            
            equity_curve.append(current_equity)
        
        # Close final position
        if position != 0 and trades:
            final_price = df['close'].iloc[-1] if 'close' in df.columns else df['rate'].iloc[-1]
            if position == 1:
                pnl = position_size * (final_price - trades[-1]['entry_price'])
            else:
                pnl = position_size * (trades[-1]['entry_price'] - final_price)
            capital += pnl - abs(pnl * commission)
        
        # Calculate metrics
        total_return = (capital - initial_capital) / initial_capital * 100
        equity_series = pd.Series(equity_curve)
        max_drawdown = (equity_series.cummax() - equity_series).max() / equity_series.cummax().max() * 100
        win_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
        win_rate = win_trades / len(trades) * 100 if trades else 0
        
        return {
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'win_rate': win_rate,
            'equity_curve': equity_curve,
            'trades': trades
        }


class SignalAlertSystem:
    """Alert system for signal triggers."""
    
    def __init__(self, config_path: str = "config/signals.yml"):
        """
        Initialize alert system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.alerts = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load alert configuration."""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('alerts', {})
        return {}
    
    def check_alert_conditions(self, signal: TradingSignal) -> List[Dict[str, Any]]:
        """
        Check if signal meets alert conditions.
        
        Args:
            signal: TradingSignal to check
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        # Check for strong signals
        if signal.strength == SignalStrength.STRONG:
            triggered_alerts.append({
                'type': 'strong_signal',
                'message': f"Strong {signal.signal_type.value} signal detected",
                'signal': signal.to_dict()
            })
        
        # Check for high confidence
        if signal.confidence >= 0.9:
            triggered_alerts.append({
                'type': 'high_confidence',
                'message': f"High confidence signal ({signal.confidence:.2f})",
                'signal': signal.to_dict()
            })
        
        # Check for extreme RSI
        rsi = signal.indicators.get('rsi', 50)
        if rsi < 20:
            triggered_alerts.append({
                'type': 'extreme_oversold',
                'message': f"Extreme oversold condition (RSI: {rsi:.2f})",
                'signal': signal.to_dict()
            })
        elif rsi > 80:
            triggered_alerts.append({
                'type': 'extreme_overbought',
                'message': f"Extreme overbought condition (RSI: {rsi:.2f})",
                'signal': signal.to_dict()
            })
        
        # Check for high ADX (strong trend)
        adx = signal.indicators.get('adx', 0)
        if adx > 40:
            triggered_alerts.append({
                'type': 'strong_trend',
                'message': f"Strong trend detected (ADX: {adx:.2f})",
                'signal': signal.to_dict()
            })
        
        return triggered_alerts
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Send an alert (placeholder for actual notification system).
        
        Args:
            alert: Alert dictionary
            
        Returns:
            True if alert sent successfully
        """
        # In production, this would integrate with email, SMS, webhooks, etc.
        print(f"ALERT: {alert['message']}")
        self.alerts.append(alert)
        return True


def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate data quality for signal generation.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Validation result dictionary
    """
    validation = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check for empty data
    if df.empty:
        validation['is_valid'] = False
        validation['errors'].append("DataFrame is empty")
        return validation
    
    # Check for minimum data points
    if len(df) < 50:
        validation['warnings'].append(
            f"Insufficient data points: {len(df)} (recommended: 50+)"
        )
    
    # Check for required columns
    required_cols = ['close', 'high', 'low', 'volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        validation['warnings'].append(
            f"Missing columns: {missing_cols}"
        )
    
    # Check for null values
    null_counts = df.isnull().sum()
    if null_counts.any():
        validation['warnings'].append(
            f"Null values detected: {null_counts[null_counts > 0].to_dict()}"
        )
    
    # Check for duplicate dates
    if df.index.duplicated().any():
        validation['warnings'].append("Duplicate dates detected")
    
    # Check for negative prices
    price_cols = ['open', 'high', 'low', 'close', 'rate', 'price']
    for col in price_cols:
        if col in df.columns and (df[col] < 0).any():
            validation['errors'].append(f"Negative values in {col}")
            validation['is_valid'] = False
    
    return validation
