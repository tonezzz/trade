"""
Tests for the trading signal generation system.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from src.signals import (
    TechnicalIndicators, SignalGenerator, SignalType, SignalStrength,
    TradingSignal, SignalHistory, Backtester, SignalAlertSystem, validate_data_quality
)


class TestTechnicalIndicators:
    """Test technical indicator calculations."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample price data for testing."""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        df = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(100) * 0.2,
            'high': prices + np.abs(np.random.randn(100) * 0.5),
            'low': prices - np.abs(np.random.randn(100) * 0.5),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        })
        df.set_index('date', inplace=True)
        return df
    
    def test_sma(self, sample_data):
        """Test Simple Moving Average calculation."""
        sma_20 = TechnicalIndicators.sma(sample_data['close'], 20)
        assert len(sma_20) == len(sample_data)
        assert sma_20.isna().sum() < 20  # First few values may be NaN
        assert sma_20.iloc[-1] > 0
    
    def test_ema(self, sample_data):
        """Test Exponential Moving Average calculation."""
        ema_12 = TechnicalIndicators.ema(sample_data['close'], 12)
        assert len(ema_12) == len(sample_data)
        assert ema_12.iloc[-1] > 0
    
    def test_rsi(self, sample_data):
        """Test RSI calculation."""
        rsi = TechnicalIndicators.rsi(sample_data['close'], 14)
        assert len(rsi) == len(sample_data)
        # RSI should be between 0 and 100
        assert rsi.dropna().between(0, 100).all()
    
    def test_macd(self, sample_data):
        """Test MACD calculation."""
        macd_result = TechnicalIndicators.macd(sample_data['close'])
        assert 'macd' in macd_result
        assert 'signal' in macd_result
        assert 'histogram' in macd_result
        assert len(macd_result['macd']) == len(sample_data)
    
    def test_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation."""
        bb_result = TechnicalIndicators.bollinger_bands(sample_data['close'])
        assert 'upper' in bb_result
        assert 'middle' in bb_result
        assert 'lower' in bb_result
        # Upper band should be >= middle >= lower (excluding NaN)
        valid_data = ~(bb_result['upper'].isna() | bb_result['middle'].isna() | bb_result['lower'].isna())
        assert (bb_result['upper'][valid_data] >= bb_result['middle'][valid_data]).all()
        assert (bb_result['middle'][valid_data] >= bb_result['lower'][valid_data]).all()
    
    def test_support_resistance(self, sample_data):
        """Test Support/Resistance calculation."""
        sr_result = TechnicalIndicators.support_resistance(sample_data['close'])
        assert 'support' in sr_result
        assert 'resistance' in sr_result
        assert len(sr_result['support']) > 0
        assert len(sr_result['resistance']) > 0
    
    def test_adx(self, sample_data):
        """Test ADX calculation."""
        adx_result = TechnicalIndicators.adx(
            sample_data['high'],
            sample_data['low'],
            sample_data['close']
        )
        assert 'adx' in adx_result
        assert 'plus_di' in adx_result
        assert 'minus_di' in adx_result
        # ADX should be between 0 and 100
        assert adx_result['adx'].dropna().between(0, 100).all()
    
    def test_volume_sma(self, sample_data):
        """Test Volume SMA calculation."""
        vol_sma = TechnicalIndicators.volume_sma(sample_data['volume'], 20)
        assert len(vol_sma) == len(sample_data)
        assert vol_sma.iloc[-1] > 0
    
    def test_volume_ratio(self, sample_data):
        """Test Volume Ratio calculation."""
        vol_ratio = TechnicalIndicators.volume_ratio(sample_data['volume'], 20)
        assert len(vol_ratio) == len(sample_data)
        # Volume ratio should be positive
        assert (vol_ratio > 0).all()
    
    def test_on_balance_volume(self, sample_data):
        """Test On Balance Volume calculation."""
        obv = TechnicalIndicators.on_balance_volume(sample_data['close'], sample_data['volume'])
        assert len(obv) == len(sample_data)
        assert obv.iloc[0] == sample_data['volume'].iloc[0]


class TestSignalGenerator:
    """Test signal generation functionality."""
    
    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data for testing."""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        df = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(100) * 0.2,
            'high': prices + np.abs(np.random.randn(100) * 0.5),
            'low': prices - np.abs(np.random.randn(100) * 0.5),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        })
        df.set_index('date', inplace=True)
        return df
    
    def test_signal_generator_init(self):
        """Test SignalGenerator initialization."""
        generator = SignalGenerator()
        assert generator.config is not None
        assert generator.indicators is not None
    
    def test_calculate_all_indicators(self, sample_ohlcv_data):
        """Test calculation of all indicators."""
        generator = SignalGenerator()
        indicators = generator.calculate_all_indicators(sample_ohlcv_data)
        
        # Check for expected indicators
        expected_indicators = [
            'sma_short', 'sma_long', 'ema_short', 'ema_long',
            'rsi', 'macd', 'macd_signal', 'macd_histogram',
            'bb_upper', 'bb_middle', 'bb_lower',
            'support', 'resistance', 'adx', 'plus_di', 'minus_di',
            'volume_sma', 'volume_ratio', 'obv'
        ]
        
        for ind in expected_indicators:
            assert ind in indicators
    
    def test_generate_signal(self, sample_ohlcv_data):
        """Test signal generation."""
        generator = SignalGenerator()
        signal = generator.generate_signal(sample_ohlcv_data)
        
        assert isinstance(signal, TradingSignal)
        assert signal.signal_type in [SignalType.BUY, SignalType.SELL, SignalType.HOLD]
        assert signal.strength in [SignalStrength.WEAK, SignalStrength.MODERATE, SignalStrength.STRONG]
        assert 0 <= signal.confidence <= 1
        assert signal.price > 0
        assert len(signal.indicators) > 0
        assert isinstance(signal.reasons, list)
    
    def test_generate_signal_insufficient_data(self):
        """Test signal generation with insufficient data."""
        generator = SignalGenerator()
        small_df = pd.DataFrame({
            'close': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'volume': [1000, 1100, 1200]
        })
        
        signal = generator.generate_signal(small_df)
        assert signal.signal_type == SignalType.HOLD
        assert signal.confidence == 0.0
    
    def test_validate_signal(self, sample_ohlcv_data):
        """Test signal validation."""
        generator = SignalGenerator()
        signal = generator.generate_signal(sample_ohlcv_data)
        validation = generator.validate_signal(signal)
        
        assert 'is_valid' in validation
        assert 'warnings' in validation
        assert 'errors' in validation
        assert isinstance(validation['warnings'], list)
        assert isinstance(validation['errors'], list)


class TestTradingSignal:
    """Test TradingSignal dataclass."""
    
    def test_trading_signal_creation(self):
        """Test creating a TradingSignal."""
        signal = TradingSignal(
            signal_type=SignalType.BUY,
            strength=SignalStrength.STRONG,
            confidence=0.85,
            timestamp=datetime.now(),
            price=100.0,
            indicators={'rsi': 25, 'macd': 0.5},
            reasons=['RSI oversold'],
            timeframe='1d'
        )
        
        assert signal.signal_type == SignalType.BUY
        assert signal.strength == SignalStrength.STRONG
        assert signal.confidence == 0.85
        assert signal.price == 100.0
    
    def test_trading_signal_to_dict(self):
        """Test converting signal to dictionary."""
        signal = TradingSignal(
            signal_type=SignalType.SELL,
            strength=SignalStrength.MODERATE,
            confidence=0.75,
            timestamp=datetime.now(),
            price=100.0,
            timeframe='1d'
        )
        
        signal_dict = signal.to_dict()
        assert 'signal_type' in signal_dict
        assert 'strength' in signal_dict
        assert 'confidence' in signal_dict
        assert signal_dict['signal_type'] == 'sell'


class TestSignalAlertSystem:
    """Test signal alert system."""
    
    @pytest.fixture
    def sample_signal(self):
        """Create a sample signal for testing."""
        return TradingSignal(
            signal_type=SignalType.BUY,
            strength=SignalStrength.STRONG,
            confidence=0.95,
            timestamp=datetime.now(),
            price=100.0,
            indicators={'rsi': 15, 'adx': 45},
            reasons=['Strong buy signal'],
            timeframe='1d'
        )
    
    def test_alert_system_init(self):
        """Test alert system initialization."""
        alert_system = SignalAlertSystem()
        assert alert_system.config is not None
        assert alert_system.alerts == []
    
    def test_check_alert_conditions_strong_signal(self, sample_signal):
        """Test alert condition for strong signal."""
        alert_system = SignalAlertSystem()
        alerts = alert_system.check_alert_conditions(sample_signal)
        
        assert len(alerts) > 0
        assert any(a['type'] == 'strong_signal' for a in alerts)
    
    def test_check_alert_conditions_high_confidence(self, sample_signal):
        """Test alert condition for high confidence."""
        alert_system = SignalAlertSystem()
        alerts = alert_system.check_alert_conditions(sample_signal)
        
        assert any(a['type'] == 'high_confidence' for a in alerts)
    
    def test_check_alert_conditions_extreme_rsi(self):
        """Test alert condition for extreme RSI."""
        signal = TradingSignal(
            signal_type=SignalType.BUY,
            strength=SignalStrength.STRONG,
            confidence=0.9,
            timestamp=datetime.now(),
            price=100.0,
            indicators={'rsi': 18},
            timeframe='1d'
        )
        
        alert_system = SignalAlertSystem()
        alerts = alert_system.check_alert_conditions(signal)
        
        assert any(a['type'] == 'extreme_oversold' for a in alerts)


class TestDataValidation:
    """Test data quality validation."""
    
    def test_validate_data_quality_valid(self):
        """Test validation with valid data."""
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104],
            'high': [101, 102, 103, 104, 105],
            'low': [99, 100, 101, 102, 103],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        validation = validate_data_quality(df)
        assert validation['is_valid'] == True
    
    def test_validate_data_quality_empty(self):
        """Test validation with empty data."""
        df = pd.DataFrame()
        validation = validate_data_quality(df)
        
        assert validation['is_valid'] == False
        assert len(validation['errors']) > 0
    
    def test_validate_data_quality_insufficient_points(self):
        """Test validation with insufficient data points."""
        df = pd.DataFrame({
            'close': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'volume': [1000, 1100, 1200]
        })
        
        validation = validate_data_quality(df)
        assert len(validation['warnings']) > 0
    
    def test_validate_data_quality_negative_prices(self):
        """Test validation with negative prices."""
        df = pd.DataFrame({
            'close': [100, -101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'volume': [1000, 1100, 1200]
        })
        
        validation = validate_data_quality(df)
        assert validation['is_valid'] == False
        assert any('negative' in err.lower() for err in validation['errors'])


class TestBacktester:
    """Test backtesting functionality."""
    
    @pytest.fixture
    def sample_backtest_data(self):
        """Create sample data for backtesting."""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        prices = 100 + np.cumsum(np.random.randn(200) * 0.3)
        
        df = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(200) * 0.2,
            'high': prices + np.abs(np.random.randn(200) * 0.5),
            'low': prices - np.abs(np.random.randn(200) * 0.5),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 200)
        })
        df.set_index('date', inplace=True)
        return df
    
    def test_backtester_init(self):
        """Test backtester initialization."""
        generator = SignalGenerator()
        backtester = Backtester(generator)
        assert backtester.generator is not None
    
    def test_run_backtest(self, sample_backtest_data):
        """Test running a backtest."""
        generator = SignalGenerator()
        backtester = Backtester(generator)
        results = backtester.run_backtest(sample_backtest_data)
        
        assert 'initial_capital' in results
        assert 'final_capital' in results
        assert 'total_return' in results
        assert 'max_drawdown' in results
        assert 'total_trades' in results
        assert 'win_rate' in results
        assert results['initial_capital'] == 10000.0
    
    def test_run_backtest_insufficient_data(self):
        """Test backtest with insufficient data."""
        generator = SignalGenerator()
        backtester = Backtester(generator)
        
        small_df = pd.DataFrame({
            'close': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'volume': [1000, 1100, 1200]
        })
        
        results = backtester.run_backtest(small_df)
        assert 'error' in results


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
