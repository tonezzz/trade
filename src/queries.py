"""
Query and analysis functions for dollar price data.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, extract
from src.models import ExchangeRate, DollarIndex, CommodityPrice
from src.database import get_db
import pandas as pd


class PriceQueries:
    """Query functions for price data."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_exchange_rates(self, 
                          quote_currency: str, 
                          start_date: Optional[date] = None, 
                          end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Get exchange rates for a specific currency.
        
        Args:
            quote_currency: Currency code (e.g., EUR, GBP, JPY)
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            DataFrame with exchange rate data
        """
        query = self.session.query(ExchangeRate).filter(
            ExchangeRate.quote_currency == quote_currency.upper()
        )
        
        if start_date:
            query = query.filter(ExchangeRate.date >= start_date)
        if end_date:
            query = query.filter(ExchangeRate.date <= end_date)
        
        query = query.order_by(ExchangeRate.date)
        
        results = query.all()
        data = [{
            'date': r.date,
            'rate': r.rate,
            'open': r.open_price,
            'high': r.high_price,
            'low': r.low_price,
            'close': r.close_price,
            'volume': r.volume
        } for r in results]
        
        return pd.DataFrame(data)
    
    def get_latest_exchange_rate(self, quote_currency: str) -> Optional[ExchangeRate]:
        """Get the latest exchange rate for a currency."""
        return self.session.query(ExchangeRate).filter(
            ExchangeRate.quote_currency == quote_currency.upper()
        ).order_by(desc(ExchangeRate.date)).first()
    
    def get_dollar_index(self, 
                       start_date: Optional[date] = None, 
                       end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Get Dollar Index (DXY) data.
        
        Args:
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            DataFrame with DXY data
        """
        query = self.session.query(DollarIndex)
        
        if start_date:
            query = query.filter(DollarIndex.date >= start_date)
        if end_date:
            query = query.filter(DollarIndex.date <= end_date)
        
        query = query.order_by(DollarIndex.date)
        
        results = query.all()
        data = [{
            'date': r.date,
            'value': r.value,
            'open': r.open_price,
            'high': r.high_price,
            'low': r.low_price,
            'close': r.close_price,
            'volume': r.volume
        } for r in results]
        
        return pd.DataFrame(data)
    
    def get_latest_dollar_index(self) -> Optional[DollarIndex]:
        """Get the latest Dollar Index value."""
        return self.session.query(DollarIndex).order_by(desc(DollarIndex.date)).first()
    
    def get_commodity_prices(self, 
                            commodity: Optional[str] = None,
                            symbol: Optional[str] = None,
                            start_date: Optional[date] = None, 
                            end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Get commodity prices.
        
        Args:
            commodity: Commodity name (e.g., GOLD, OIL)
            symbol: Trading symbol (e.g., XAUUSD, USOIL)
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            DataFrame with commodity price data
        """
        query = self.session.query(CommodityPrice)
        
        if commodity:
            query = query.filter(CommodityPrice.commodity == commodity.upper())
        if symbol:
            query = query.filter(CommodityPrice.symbol == symbol.upper())
        if start_date:
            query = query.filter(CommodityPrice.date >= start_date)
        if end_date:
            query = query.filter(CommodityPrice.date <= end_date)
        
        query = query.order_by(CommodityPrice.date)
        
        results = query.all()
        data = [{
            'date': r.date,
            'commodity': r.commodity,
            'symbol': r.symbol,
            'price': r.price,
            'unit': r.unit,
            'open': r.open_price,
            'high': r.high_price,
            'low': r.low_price,
            'close': r.close_price,
            'volume': r.volume
        } for r in results]
        
        return pd.DataFrame(data)
    
    def get_latest_commodity_price(self, commodity: Optional[str] = None, 
                                  symbol: Optional[str] = None) -> Optional[CommodityPrice]:
        """Get the latest commodity price."""
        query = self.session.query(CommodityPrice)
        
        if commodity:
            query = query.filter(CommodityPrice.commodity == commodity.upper())
        if symbol:
            query = query.filter(CommodityPrice.symbol == symbol.upper())
        
        return query.order_by(desc(CommodityPrice.date)).first()


class PriceAnalysis:
    """Analysis functions for price data."""
    
    def __init__(self, session: Session):
        self.session = session
        self.queries = PriceQueries(session)
    
    def calculate_currency_performance(self, 
                                      quote_currency: str, 
                                      start_date: date, 
                                      end_date: date) -> Dict[str, Any]:
        """
        Calculate currency performance over a period.
        
        Args:
            quote_currency: Currency code
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with performance metrics
        """
        df = self.queries.get_exchange_rates(quote_currency, start_date, end_date)
        
        if df.empty:
            return {}
        
        start_rate = df.iloc[0]['rate']
        end_rate = df.iloc[-1]['rate']
        change = end_rate - start_rate
        change_percent = (change / start_rate) * 100
        
        high = df['high'].max() if 'high' in df.columns else df['rate'].max()
        low = df['low'].min() if 'low' in df.columns else df['rate'].min()
        
        return {
            'currency': quote_currency,
            'start_date': start_date,
            'end_date': end_date,
            'start_rate': start_rate,
            'end_rate': end_rate,
            'change': change,
            'change_percent': change_percent,
            'high': high,
            'low': low,
            'range': high - low
        }
    
    def calculate_dxy_performance(self, 
                                  start_date: date, 
                                  end_date: date) -> Dict[str, Any]:
        """
        Calculate Dollar Index performance over a period.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with performance metrics
        """
        df = self.queries.get_dollar_index(start_date, end_date)
        
        if df.empty:
            return {}
        
        start_value = df.iloc[0]['value']
        end_value = df.iloc[-1]['value']
        change = end_value - start_value
        change_percent = (change / start_value) * 100
        
        high = df['high'].max() if 'high' in df.columns else df['value'].max()
        low = df['low'].min() if 'low' in df.columns else df['value'].min()
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'start_value': start_value,
            'end_value': end_value,
            'change': change,
            'change_percent': change_percent,
            'high': high,
            'low': low,
            'range': high - low
        }
    
    def get_available_currencies(self) -> List[str]:
        """Get list of available currencies in database."""
        currencies = self.session.query(ExchangeRate.quote_currency).distinct().all()
        return [c[0] for c in currencies]
    
    def get_available_commodities(self) -> List[str]:
        """Get list of available commodities in database."""
        commodities = self.session.query(CommodityPrice.commodity).distinct().all()
        return [c[0] for c in commodities]
    
    def get_date_range(self, model_class) -> Dict[str, date]:
        """Get the date range for a given model."""
        min_date = self.session.query(func.min(model_class.date)).scalar()
        max_date = self.session.query(func.max(model_class.date)).scalar()
        
        return {
            'min_date': min_date,
            'max_date': max_date
        }


def get_queries() -> PriceQueries:
    """Get a PriceQueries instance with database session."""
    session = next(get_db())
    return PriceQueries(session)


def get_analysis() -> PriceAnalysis:
    """Get a PriceAnalysis instance with database session."""
    session = next(get_db())
    return PriceAnalysis(session)
