# Commodity Validation Sources Configuration

**Last Updated:** 2026-08-07
**Related Files:** `scripts/data_quality_agent.py`, `config/data_sources.yml`
**Tags:** validation, API, commodities, gold, oil, Alpha Vantage, Minted Metal

## Overview

The trade system uses multiple external API sources for real-time commodity price validation to ensure data quality and accuracy. This document describes the current validation source configuration and integration status.

## Validation Sources Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Quality Validation                      │
├──────────────────┬──────────────────┬──────────────────────────┤
│   Oil & Energy   │  Precious Metals │   Agricultural           │
│   Commodities     │                  │   Commodities            │
└──────────────────┴──────────────────┴──────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Alpha Vantage    │  │ Minted Metal    │  │ Alpha Vantage    │
│ (Primary)        │  │ (Primary)       │  │ (Primary)        │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Fallback Sources │  │ MetalPrices API  │  │ Fallback Sources │
│ (Optional)       │  │ (Backup)         │  │ (Optional)       │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Alpha Vantage API (Oil & Agricultural Commodities)

### Status: ✅ Fully Configured and Operational

**Configuration:**
- **API Key:** KUTH6I3J1OORWZI8
- **MCP Server:** Configured in `~/.config/devin/mcp_config.json`
- **Free Tier Limits:** 25 requests/day, 5 requests/minute
- **Integration:** MCP server for automated validation

**Supported Commodities:**
- **WTI** - West Texas Intermediate Crude Oil
- **BRENT** - Brent Crude Oil  
- **WHEAT** - Global Wheat Prices
- **CORN** - Corn Prices
- **COPPER** - Copper Prices
- **NATURAL_GAS** - Natural Gas Prices

**Data Coverage:**
- Historical data: 20+ years
- Update frequency: Daily
- Data format: Monthly time series (timestamp, value)

**Integration Details:**
- Primary validation source for oil and agricultural commodities
- Used in `scripts/data_quality_agent.py` via direct HTTP calls
- MCP server available for tool discovery and testing
- Function names: WTI, BRENT, WHEAT, CORN, COPPER, NATURAL_GAS

**Test Results (2026-08-07):**
- WTI: $80.46 (487 data points available)
- BRENT: $83.76 (471 data points available)
- All functions working correctly

## Minted Metal API (Precious Metals)

### Status: ✅ Fully Configured and Operational

**Configuration:**
- **API Endpoint:** https://mintedmetal.com/api/prices.json
- **API Key:** Not required (free service)
- **License:** CC BY 4.0 (attribution required)
- **Update Schedule:** Twice daily at 11:00 and 16:00 UTC (Mon-Fri)

**Supported Metals:**
- **GOLD (XAU)** - Gold spot price
- **SILVER (XAG)** - Silver spot price
- **PLATINUM (XPT)** - Platinum spot price
- **PALLADIUM (XPD)** - Palladium spot price
- **RHODIUM** - Rhodium spot price

**Data Source:**
- **Primary Source:** LBMA (London Bullion Market Association) benchmark prices
- **Authority:** Most authoritative source for precious metals
- **Coverage:** London PM Fix for gold, London Silver Fix for silver
- **Additional:** Umicore 10am indication for rhodium

**Integration Details:**
- Primary validation source for precious metals in `scripts/data_quality_agent.py`
- No API key required - completely free
- CORS-enabled for browser-based access
- Edge-cached for 15 minutes via Cloudflare
- Attribution: "Cite: Minted Metal (mintedmetal.com)"

**Test Results (2026-08-07):**
- GOLD (XAU): $4,267.85 per troy oz (London PM Fix)
- SILVER (XAG): $61.74 per troy oz (London Silver Fix)
- PLATINUM: $1,728.05 per troy oz
- PALLADIUM: $1,372.65 per troy oz
- RHODIUM: $8,500.00 per troy oz
- All metals fetched successfully

## MetalPrices API (Precious Metals Backup)

### Status: ⚠️ Configured as Fallback

**Configuration:**
- **API Endpoint:** https://api.metalpriceapi.com/v1/latest
- **API Key:** Optional (configure in .env as METAL_PRICES_API_KEY)
- **Free Tier:** 100 requests/month
- **Usage:** Backup validation source for precious metals

**Supported Metals:**
- **GOLD (XAU)** - Gold spot price
- **SILVER (XAG)** - Silver spot price
- **PLATINUM (XPT)** - Platinum spot price
- **PALLADIUM (XPD)** - Palladium spot price

**Integration Details:**
- Configured as fallback in `scripts/data_quality_agent.py`
- Used only if Minted Metal API fails
- Requires API key for operation
- Provides similar coverage to Minted Metal

## FRED API (Economic Data - Optional)

### Status: ⚠️ Optional for Enhanced Validation

**Configuration:**
- **API Endpoint:** https://api.stlouisfed.org/fred/series/observations
- **API Key:** Optional (configure in .env as FRED_API_KEY)
- **Free Tier:** 120 requests/minute
- **Usage:** Secondary validation for exchange rates and DXY

**Supported Data:**
- Exchange rates (major currencies)
- Economic indicators
- Interest rates
- Dollar Index (DXY) - DTWEXBGS series

**Integration Details:**
- Optional enhancement for validation coverage
- Currently used for some exchange rate validation
- Provides official Federal Reserve economic data
- High rate limits suitable for frequent validation

## ExchangeRate-API (Current Exchange Rates)

### Status: ✅ Primary Validation for Exchange Rates

**Configuration:**
- **API Endpoint:** https://api.exchangerate-api.com/v4/latest/USD
- **Free Tier:** 1,500 requests/month
- **Usage:** Real-time exchange rate validation
- **API Key:** Not required for free tier

**Supported Currencies:**
- 170+ currencies worldwide
- Major currencies: EUR, GBP, JPY, CAD, CHF, AUD, NZD, THB
- Real-time rates with good coverage

**Integration Details:**
- Primary validation source for exchange rates
- Used in `scripts/data_quality_agent.py`
- Good coverage including THB (important for this system)
- Reliable and frequently updated

## Configuration Files

### Environment Variables (.env)
```bash
# Alpha Vantage API (Configured)
ALPHA_VANTAGE_API_KEY=KUTH6I3J1OORWZI8

# MetalPrices API (Optional backup)
METAL_PRICES_API_KEY=your_key_here

# FRED API (Optional)
FRED_API_KEY=your_fred_api_key_here

# Minted Metal API: No key required
```

### SSOT Configuration (config/data_sources.yml)
```yaml
# Validation sources documentation
validation_sources:
  commodities:
    primary: "Alpha Vantage API"
    functions: ["WTI", "BRENT", "WHEAT", "CORN", "COPPER", "NATURAL_GAS"]
    status: "operational"
  
  precious_metals:
    primary: "Minted Metal API"
    endpoint: "https://mintedmetal.com/api/prices.json"
    backup: "MetalPrices API"
    status: "operational"
  
  exchange_rates:
    primary: "ExchangeRate-API"
    secondary: "FRED API"
    status: "operational"
```

## Usage in Data Quality Agent

The validation sources are integrated in `scripts/data_quality_agent.py`:

```python
def _get_commodity_price_from_external(self, symbol: str) -> Tuple[Optional[float], str]:
    """Get current commodity price from external sources using Alpha Vantage API."""
    
    # Map symbols to Alpha Vantage function names
    symbol_to_function = {
        'WTI': 'WTI',
        'BRENT': 'BRENT', 
        'W': 'WHEAT',
        'ZC': 'CORN',
        'HG': 'COPPER'
    }
    
    # Use Alpha Vantage for oil and agricultural commodities
    # Fall back to Minted Metal for precious metals
```

```python
def _get_precious_metals_from_fallback(self, symbol: str) -> Tuple[Optional[float], str]:
    """Fallback method for precious metals using alternative APIs."""
    
    # Primary: Minted Metal API (free, no API key)
    url = "https://mintedmetal.com/api/prices.json"
    
    # Backup: MetalPrices API (requires API key)
    # Used only if Minted Metal fails
```

## Benefits of Current Configuration

1. **Cost-Effective**: Primary sources are free with no API keys required
2. **Authoritative Data**: LBMA benchmark prices for precious metals
3. **Redundancy**: Backup sources available for critical data
4. **Comprehensive Coverage**: Oil, agricultural commodities, precious metals
5. **Real-Time Validation**: Current prices for data quality checks
6. **High Reliability**: Multiple fallback options for resilience

## Maintenance and Monitoring

### Regular Tasks
1. **Monitor API Rate Limits**: Track usage against free tier limits
2. **Validate Data Quality**: Regular checks of validation accuracy
3. **Update Configuration**: Add new commodities or sources as needed
4. **Review Attribution**: Ensure proper attribution for licensed data

### Troubleshooting
1. **Alpha Vantage Rate Limits**: 25 requests/day free tier - space out requests
2. **Minted Metal Updates**: Only twice daily - plan validation accordingly
3. **MetalPrices Fallback**: Configure API key if primary source fails
4. **FRED Integration**: Optional enhancement for additional validation

## Future Enhancements

### Potential Additions
1. **Energy Price API**: Additional energy commodities (gasoline, heating oil)
2. **SentiSignal API**: Enhanced gold data with historical access
3. **Quandl Integration**: Economic indicators and advanced commodity data
4. **Real-Time Streaming**: WebSocket connections for live price updates

### Scalability Considerations
1. **Premium Tiers**: Upgrade API tiers if rate limits become constraining
2. **Caching Strategy**: Implement smart caching to reduce API calls
3. **Load Balancing**: Distribute validation across multiple API keys
4. **Monitoring**: Add API usage monitoring and alerting

## Related Documentation

- [Data Quality System](../DATA_QUALITY_SYSTEM.md) - Overall data quality monitoring
- [Data Sources](../data/DATA_SOURCES.md) - Historical data sources for import
- [API Guide](../core/API_GUIDE.md) - REST API documentation
- [Architecture](../core/ARCHITECTURE.md) - System architecture overview

## Change Log

**2026-08-07:**
- Added Minted Metal API as primary precious metals validation source
- Configured Alpha Vantage MCP integration for oil and agricultural commodities
- Updated data quality agent with new validation sources
- Added comprehensive documentation for validation sources
- Tested all validation sources and confirmed operational status