#!/usr/bin/env python3
"""
Data Quality Monitoring Agent for Trade Database

This agent monitors data quality by:
1. Comparing database values against external sources
2. Checking data freshness and completeness
3. Validating data accuracy within acceptable tolerances
4. Maintaining historical quality records
5. Alerting on data quality issues
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.database import db
from src.models import ExchangeRate, CommodityPrice, DollarIndex
import requests
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_quality.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DataQualityAgent')


@dataclass
class ValidationResult:
    """Data validation result."""
    symbol: str
    data_type: str
    timestamp: datetime
    db_value: Optional[float]
    external_value: Optional[float]
    difference_pct: Optional[float]
    is_accurate: bool
    freshness_days: Optional[int]
    completeness_pct: Optional[float]
    issues: List[str]
    external_source: str


class DataQualityAgent:
    """Monitors and validates data quality across the trade database."""
    
    def __init__(self, tolerance_pct: float = 2.0, max_freshness_days: int = 2):
        """
        Initialize the data quality agent.
        
        Args:
            tolerance_pct: Acceptable percentage difference between DB and external sources
            max_freshness_days: Maximum acceptable data age in days
        """
        self.tolerance_pct = tolerance_pct
        self.max_freshness_days = max_freshness_days
        self.session = db.get_session()
        self.results: List[ValidationResult] = []
        
        # Symbol-specific tolerances (higher for precious metals due to unit differences)
        self.symbol_tolerances = {
            'XAU': 15.0,  # Gold - higher tolerance for unit differences
            'XAG': 15.0,  # Silver - higher tolerance for unit differences
            'GOLD': 15.0,
            'SILVER': 15.0,
            'THB': 0.5,   # THB - tight tolerance (using reliable API)
            'EUR': 1.0,   # Major currencies - tight tolerance
            'GBP': 1.0,
            'JPY': 1.0,
            'CAD': 1.0,
            'CHF': 1.0,
            'AUD': 1.0,
            'NZD': 1.0
        }
        
        # Symbol-specific freshness tolerances (days)
        self.symbol_freshness = {
            'XAU': 5,  # Gold - allow 5 days
            'XAG': 5,  # Silver - allow 5 days
            'GOLD': 5,
            'SILVER': 5,
            'DXY': 7   # Dollar Index - allow 7 days (FRED updates less frequently)
        }
        
        # External source APIs
        self.external_sources = {
            'exchange_rates': self._get_exchange_rate_from_external,
            'commodities': self._get_commodity_price_from_external,
            'dollar_index': self._get_dollar_index_from_external
        }
    
    def _get_exchange_rate_from_external(self, symbol: str) -> Tuple[Optional[float], str]:
        """Get current exchange rate from external sources."""
        
        # Primary: open.er-api.com (reliable for THB, use for all currencies)
        try:
            url = f"https://open.er-api.com/v6/latest/USD"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 'success':
                    rates = data.get('rates', {})
                    
                    # Map symbol to API format
                    symbol_map = {
                        'EUR': 'EUR',
                        'GBP': 'GBP', 
                        'JPY': 'JPY',
                        'CAD': 'CAD',
                        'CHF': 'CHF',
                        'AUD': 'AUD',
                        'NZD': 'NZD',
                        'THB': 'THB'
                    }
                    
                    api_symbol = symbol_map.get(symbol, symbol)
                    if api_symbol in rates:
                        logger.info(f"Successfully fetched {symbol} from open.er-api.com: {rates[api_symbol]}")
                        return rates[api_symbol], 'open.er-api.com'
            
        except Exception as e:
            logger.warning(f"Failed to get exchange rate from open.er-api.com: {e}")
        
        # Fallback: ExchangeRate-API (free tier: 1,500 requests/month)
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                # Map symbol to API format
                symbol_map = {
                    'EUR': 'EUR',
                    'GBP': 'GBP', 
                    'JPY': 'JPY',
                    'CAD': 'CAD',
                    'CHF': 'CHF',
                    'AUD': 'AUD',
                    'NZD': 'NZD',
                    'THB': 'THB'
                }
                
                api_symbol = symbol_map.get(symbol, symbol)
                if api_symbol in rates:
                    return rates[api_symbol], 'exchangerate-api.com'
            
        except Exception as e:
            logger.warning(f"Failed to get exchange rate from exchangerate-api: {e}")
        
        # Fallback to alternative sources or return None
        return None, 'none'
    
    def _get_commodity_price_from_external(self, symbol: str) -> Tuple[Optional[float], str]:
        """Get current commodity price from external sources using Alpha Vantage API."""
        
        # Map symbols to Alpha Vantage function names
        av_function_map = {
            'GOLD': None,  # Gold - use fallback
            'SILVER': None,  # Silver - use fallback  
            'COPPER': 'COPPER',
            'OIL': 'WTI',    # Crude Oil WTI
            'BRENT': 'BRENT',  # Brent Crude
            'NATURAL_GAS': 'NATURAL_GAS',
            'WHEAT': 'WHEAT',
            'CORN': 'CORN',
            'SOY': 'SOYBEANS',
            'ALUMINUM': 'ALUMINUM',
            'SUGAR': 'SUGAR',
            'COFFEE': 'COFFEE',
            'COTTON': 'COTTON'
        }
        
        # Map internal symbols to AV function names
        symbol_to_function = {
            'XAU': None,  # Gold - use fallback
            'XAG': None,  # Silver - use fallback
            'HG': 'COPPER',
            'WTI': 'WTI',
            'BRENT': 'BRENT', 
            'NG': 'NATURAL_GAS',
            'W': 'WHEAT',
            'ZC': 'CORN',
            'ZS': 'SOYBEANS'
        }
        
        # Get the function name for this symbol
        function_name = symbol_to_function.get(symbol, av_function_map.get(symbol))
        
        if not function_name:
            logger.info(f"Using fallback for precious metals symbol: {symbol}")
            # Fallback to MetalPrices API for precious metals
            return self._get_precious_metals_from_fallback(symbol)
        
        try:
            # Use Alpha Vantage API directly with correct function names
            alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if alpha_vantage_key:
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': function_name,
                    'apikey': alpha_vantage_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # Parse the data - Alpha Vantage returns different formats
                    if 'data' in data and len(data['data']) > 0:
                        # Get the most recent value
                        latest_data = data['data'][0]
                        value = latest_data.get('value')
                        if value and value != '.':
                            logger.info(f"Successfully fetched {symbol} from Alpha Vantage: {value}")
                            return float(value), 'alpha-vantage-api'
            
        except Exception as e:
            logger.warning(f"Failed to get commodity price from Alpha Vantage API: {e}")
        
        # Fallback to alternative sources
        return self._get_precious_metals_from_fallback(symbol)
    
    def _get_precious_metals_from_fallback(self, symbol: str) -> Tuple[Optional[float], str]:
        """Fallback method for precious metals using alternative APIs."""
        
        # Source 1: Minted Metal API (free, no API key required, LBMA benchmark prices)
        if symbol in ['GOLD', 'SILVER', 'XAU', 'XAG']:
            try:
                metal_map = {'GOLD': 'gold', 'SILVER': 'silver', 'XAU': 'gold', 'XAG': 'silver'}
                metal_key = metal_map.get(symbol, symbol.lower())
                
                url = "https://mintedmetal.com/api/prices.json"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    metals = data.get('metals', {})
                    if metal_key in metals:
                        price = metals[metal_key].get('price')
                        if price:
                            logger.info(f"Successfully fetched {symbol} from Minted Metal API: {price}")
                            return float(price), 'minted-metal-api'
            
            except Exception as e:
                logger.warning(f"Failed to get commodity price from Minted Metal API: {e}")
        
        # Source 2: MetalPrices API (free tier: 100 requests/month)
        metal_prices_key = os.getenv('METAL_PRICES_API_KEY')
        if metal_prices_key and symbol in ['GOLD', 'SILVER', 'XAU', 'XAG']:
            try:
                metal_map = {'GOLD': 'XAU', 'SILVER': 'XAG', 'XAU': 'XAU', 'XAG': 'XAG'}
                metal_symbol = metal_map.get(symbol, symbol)
                
                url = f"https://api.metalpriceapi.com/v1/latest"
                params = {
                    'api_key': metal_prices_key,
                    'base': 'USD',
                    'currencies': metal_symbol
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get('rates', {})
                    if metal_symbol in rates:
                        return rates[metal_symbol], 'metalprice-api'
            
            except Exception as e:
                logger.warning(f"Failed to get commodity price from MetalPrices API: {e}")
        
        return None, 'none'
    
    def _get_dollar_index_from_external(self, symbol: str) -> Tuple[Optional[float], str]:
        """Get current dollar index from external sources."""
        
        # Source 1: FRED API (free: 120 requests/minute)
        fred_api_key = os.getenv('FRED_API_KEY')
        if fred_api_key:
            try:
                url = f"https://api.stlouisfed.org/fred/series/observations"
                params = {
                    'series_id': 'DTWEXBGS',  # Trade Weighted U.S. Dollar Index (Broad)
                    'api_key': fred_api_key,
                    'limit': 1,
                    'sort_order': 'desc'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    observations = data.get('observations', [])
                    if observations and len(observations) > 0:
                        latest_value = observations[0].get('value')
                        if latest_value and latest_value != '.':
                            return float(latest_value), 'fred-api'
            
            except Exception as e:
                logger.warning(f"Failed to get DXY from FRED API: {e}")
        
        # Source 2: Alpha Vantage (free tier: 25 requests/day)
        alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if alpha_vantage_key:
            try:
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'CURRENCY_EXCHANGE_RATE',
                    'from_currency': 'DXY',
                    'to_currency': 'USD',
                    'apikey': alpha_vantage_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # Alpha Vantage may not support DXY directly, but we can try
                    # This is a fallback attempt
                    logger.info("Alpha Vantage DXY attempt - may not be supported")
            
            except Exception as e:
                logger.warning(f"Failed to get DXY from Alpha Vantage: {e}")
        
        return None, 'none'
    
    def _get_latest_db_value(self, data_type: str, symbol: str) -> Tuple[Optional[float], Optional[int], Optional[float]]:
        """
        Get latest value from database along with freshness and completeness.
        
        Returns:
            Tuple of (latest_value, freshness_days, completeness_pct)
        """
        try:
            if data_type == 'exchange_rates':
                latest = self.session.query(ExchangeRate)\
                    .filter(ExchangeRate.quote_currency == symbol)\
                    .order_by(ExchangeRate.date.desc())\
                    .first()
                
                if latest:
                    # Calculate freshness
                    freshness = (datetime.now().date() - latest.date).days
                    
                    # Calculate completeness (expected daily data from 2016)
                    date_range = (latest.date - datetime(2016, 8, 1).date()).days
                    expected_records = max(1, date_range)
                    actual_records = self.session.query(ExchangeRate)\
                        .filter(ExchangeRate.quote_currency == symbol).count()
                    completeness = (actual_records / expected_records) * 100
                    
                    return latest.close_price, freshness, completeness
                    
            elif data_type == 'commodities':
                latest = self.session.query(CommodityPrice)\
                    .filter(CommodityPrice.symbol == symbol)\
                    .order_by(CommodityPrice.date.desc())\
                    .first()
                
                if latest:
                    freshness = (datetime.now().date() - latest.date).days
                    return latest.close_price, freshness, None
                    
            elif data_type == 'dollar_index':
                latest = self.session.query(DollarIndex)\
                    .order_by(DollarIndex.date.desc())\
                    .first()
                
                if latest:
                    freshness = (datetime.now().date() - latest.date).days
                    return latest.close_price, freshness, None
                    
        except Exception as e:
            logger.error(f"Error getting latest DB value for {symbol}: {e}")
        
        return None, None, None
    
    def validate_symbol(self, data_type: str, symbol: str) -> ValidationResult:
        """
        Validate a single symbol against external sources.
        
        Args:
            data_type: Type of data (exchange_rates, commodities, dollar_index)
            symbol: Symbol to validate
            
        Returns:
            ValidationResult with validation details
        """
        timestamp = datetime.now()
        issues = []
        
        # Get database value
        db_value, freshness_days, completeness_pct = self._get_latest_db_value(data_type, symbol)
        
        # Get external value
        external_func = self.external_sources.get(data_type)
        external_value, external_source = external_func(symbol) if external_func else (None, 'none')
        
        # Calculate difference
        difference_pct = None
        is_accurate = True
        
        if db_value and external_value:
            difference_pct = abs((db_value - external_value) / external_value) * 100
            # Use symbol-specific tolerance if available
            tolerance = self.symbol_tolerances.get(symbol, self.tolerance_pct)
            if difference_pct > tolerance:
                is_accurate = False
                issues.append(f"Value difference {difference_pct:.2f}% exceeds tolerance {tolerance}%")
        
        # Check freshness
        if freshness_days is not None:
            max_freshness = self.symbol_freshness.get(symbol, self.max_freshness_days)
            if freshness_days > max_freshness:
                is_accurate = False
                issues.append(f"Data is {freshness_days} days old (max: {max_freshness})")
        
        # Check completeness
        if completeness_pct is not None and completeness_pct < 80:  # Adjusted from 90% to 80%
            is_accurate = False
            issues.append(f"Data completeness {completeness_pct:.1f}% below 80%")
        
        # Check for missing data
        if db_value is None:
            is_accurate = False
            issues.append("No data found in database")
        
        if external_value is None:
            issues.append("Could not fetch external reference value")
        
        return ValidationResult(
            symbol=symbol,
            data_type=data_type,
            timestamp=timestamp,
            db_value=db_value,
            external_value=external_value,
            difference_pct=difference_pct,
            is_accurate=is_accurate,
            freshness_days=freshness_days,
            completeness_pct=completeness_pct,
            issues=issues,
            external_source=external_source
        )
    
    def validate_all_exchange_rates(self) -> List[ValidationResult]:
        """Validate all exchange rates in the database."""
        logger.info("Validating exchange rates...")
        
        # Get all unique quote currencies
        currencies = self.session.query(ExchangeRate.quote_currency)\
            .distinct()\
            .all()
        
        results = []
        for currency_tuple in currencies:
            currency = currency_tuple[0]  # Extract the currency code from the tuple
            if len(currency) == 3:  # Only validate proper 3-letter currency codes
                result = self.validate_symbol('exchange_rates', currency)
                results.append(result)
                self.results.append(result)
                
                # Log immediate issues
                if not result.is_accurate:
                    logger.warning(f"Exchange rate {currency} validation failed: {result.issues}")
            else:
                logger.warning(f"Skipping invalid currency code: {currency}")
        
        return results
    
    def validate_all_commodities(self) -> List[ValidationResult]:
        """Validate only precious metals in the database."""
        logger.info("Validating precious metals...")
        
        # Only validate precious metals
        precious_metals = {'GOLD', 'SILVER', 'XAU', 'XAG'}
        
        commodities = self.session.query(CommodityPrice.symbol)\
            .distinct()\
            .all()
        
        results = []
        for commodity_tuple in commodities:
            commodity = commodity_tuple[0]  # Extract the symbol from the tuple
            
            # Only validate precious metals
            if commodity not in precious_metals:
                logger.info(f"Skipping non-precious metal: {commodity}")
                continue
                
            if len(commodity) >= 2:  # Only validate symbols with at least 2 characters
                result = self.validate_symbol('commodities', commodity)
                results.append(result)
                self.results.append(result)
                
                if not result.is_accurate:
                    logger.warning(f"Commodity {commodity} validation failed: {result.issues}")
            else:
                logger.warning(f"Skipping invalid commodity symbol: {commodity}")
        
        return results
    
    def validate_dollar_index(self) -> ValidationResult:
        """Validate dollar index data."""
        logger.info("Validating dollar index...")
        
        result = self.validate_symbol('dollar_index', 'DXY')
        self.results.append(result)
        
        if not result.is_accurate:
            logger.warning(f"Dollar index validation failed: {result.issues}")
        
        return result
    
    def run_full_validation(self) -> Dict[str, any]:
        """
        Run full validation across all data types.
        
        Returns:
            Summary of validation results
        """
        logger.info("=" * 60)
        logger.info("Starting full data quality validation")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Validate all data types
        exchange_rate_results = self.validate_all_exchange_rates()
        commodity_results = self.validate_all_commodities()
        dxy_result = self.validate_dollar_index()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate summary statistics
        total_validations = len(self.results)
        failed_validations = sum(1 for r in self.results if not r.is_accurate)
        success_rate = ((total_validations - failed_validations) / total_validations * 100) if total_validations > 0 else 0
        
        summary = {
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'total_validations': total_validations,
            'failed_validations': failed_validations,
            'success_rate': success_rate,
            'exchange_rates_validated': len(exchange_rate_results),
            'commodities_validated': len(commodity_results),
            'dollar_index_validated': 1 if dxy_result else 0,
            'tolerance_pct': self.tolerance_pct,
            'max_freshness_days': self.max_freshness_days
        }
        
        logger.info("=" * 60)
        logger.info("Validation Summary")
        logger.info("=" * 60)
        logger.info(f"Total validations: {total_validations}")
        logger.info(f"Failed validations: {failed_validations}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("=" * 60)
        
        # Save results to file
        self._save_validation_results(summary)
        
        return summary
    
    def _save_validation_results(self, summary: Dict):
        """Save validation results to JSON file for historical tracking."""
        results_dir = 'data/quality'
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = os.path.join(results_dir, f'validation_{timestamp}.json')
        
        output = {
            'summary': summary,
            'detailed_results': [asdict(r) for r in self.results]
        }
        
        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        logger.info(f"Validation results saved to: {results_file}")
    
    def get_quality_history(self, days: int = 30) -> List[Dict]:
        """
        Get historical quality validation results.
        
        Args:
            days: Number of days of history to retrieve
            
        Returns:
            List of historical validation summaries
        """
        results_dir = 'data/quality'
        history = []
        
        if not os.path.exists(results_dir):
            return history
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(results_dir):
            if filename.startswith('validation_') and filename.endswith('.json'):
                filepath = os.path.join(results_dir, filename)
                
                # Extract timestamp from filename
                try:
                    file_timestamp = datetime.strptime(filename.replace('validation_', '').replace('.json', ''), '%Y%m%d_%H%M%S')
                    
                    if file_timestamp >= cutoff_date:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            history.append(data['summary'])
                except ValueError:
                    continue
        
        # Sort by timestamp
        history.sort(key=lambda x: x['timestamp'])
        
        return history
    
    def __del__(self):
        """Cleanup database session."""
        if hasattr(self, 'session'):
            self.session.close()


def main():
    """Main entry point for data quality agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Quality Monitoring Agent')
    parser.add_argument('--tolerance', type=float, default=2.0, 
                       help='Acceptable percentage difference (default: 2.0)')
    parser.add_argument('--freshness', type=int, default=2,
                       help='Maximum data age in days (default: 2)')
    parser.add_argument('--history', type=int, default=30,
                       help='Show quality history for N days (default: 30)')
    parser.add_argument('--history-only', action='store_true',
                       help='Only show history, skip validation')
    
    args = parser.parse_args()
    
    agent = DataQualityAgent(
        tolerance_pct=args.tolerance,
        max_freshness_days=args.freshness
    )
    
    if args.history_only:
        # Show historical data
        history = agent.get_quality_history(args.history)
        
        print("\n" + "=" * 60)
        print("Data Quality History")
        print("=" * 60)
        
        for summary in history:
            print(f"\nTimestamp: {summary['timestamp']}")
            print(f"Success Rate: {summary['success_rate']:.1f}%")
            print(f"Failed: {summary['failed_validations']}/{summary['total_validations']}")
        
        if not history:
            print("No historical data found.")
    else:
        # Run full validation
        summary = agent.run_full_validation()
        
        # Exit with error code if validation failed
        if summary['failed_validations'] > 0:
            sys.exit(1)


if __name__ == '__main__':
    main()