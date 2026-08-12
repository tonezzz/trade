# Metal Price API Research

**Date**: 2026-08-12  
**Purpose**: Research free metal price APIs for trade service integration

## Best Free Metal Price APIs

### 1. Minted Metal API (RECOMMENDED)
- **URL**: `https://mintedmetal.com/api/prices.json`
- **Cost**: Completely free
- **API Key**: Not required
- **Rate Limit**: No hard limit (recommend 15 min polling)
- **Data**: Gold, Silver, Platinum, Palladium, Rhodium
- **Update Frequency**: Twice daily
- **License**: CC BY 4.0 (attribution required)
- **Format**: JSON with CORS enabled
- **Source**: LBMA benchmark prices

**Example Response:**
```json
{
  "metals": {
    "gold": {"price": 4794.75, "currency": "USD", "unit": "troy ounce"},
    "silver": {"price": 77.43, "currency": "USD", "unit": "troy ounce"}
  }
}
```

**Usage:**
```bash
curl https://mintedmetal.com/api/prices.json | jq '.metals.gold.price'
```

### 2. croncopia/commodity-prices (GitHub-Based)
- **URL**: `http://commodity.croncopia.com/latest/metals/gold.json`
- **Cost**: Completely free
- **API Key**: Not required
- **Rate Limit**: None
- **Data**: Multiple commodities including metals
- **Update Frequency**: Every 30 minutes
- **Access Methods**: GitHub Pages, jsDelivr CDN, raw GitHub

**Example URLs:**
- `http://commodity.croncopia.com/latest/metals/gold.json`
- `https://cdn.jsdelivr.net/gh/croncopia/commodity-prices/latest/metals/gold.json`
- `https://raw.githubusercontent.com/croncopia/commodity-prices/refs/heads/main/latest/metals/gold.json`

### 3. Metals-API.com (alebrega/metals-api)
- **Cost**: Free plan available
- **API Key**: Required (free signup)
- **Rate Limit**: Based on plan
- **Data**: Precious metals + 168 currencies
- **Update Frequency**: 60 seconds to 60 minutes

### 4. Metals.Dev
- **Cost**: Free tier (100 requests/month)
- **API Key**: Required
- **Rate Limit**: 100 requests/month free tier
- **Data**: 28+ metals + 170+ currencies
- **Update Frequency**: Real-time (60 second delay)

## Recommendation

**Use Minted Metal API** because:
- ✅ No API key required
- ✅ No rate limits
- ✅ Attribution only (easy to add)
- ✅ CORS enabled
- ✅ Reliable LBMA benchmark prices
- ✅ Simple JSON format
- ✅ Edge-cached for 15 minutes via Cloudflare

## Current Status

- ✅ Alpha Vantage API configured and working for commodities (COPPER, NATURAL_GAS)
- ❌ Metal Prices API key invalid (different service)
- ❌ Precious metals (GOLD, SILVER) not working
- ✅ Trade service health check shows healthy status with minor data gaps

## Next Steps

1. Implement Minted Metal API as new data source for precious metals
2. Replace current Metal Prices API integration in `src/data_sources/metal_prices_source.py`
3. Test precious metals download (GOLD, SILVER)
4. Update configuration to use Minted Metal API
5. Add attribution to data source metadata

## Implementation Notes

For Minted Metal API integration:
- No API key needed
- Simple GET request to `https://mintedmetal.com/api/prices.json`
- Parse JSON response for metal prices
- Map to existing commodity price format
- Add attribution in source metadata
- Respect 15-minute polling recommendation
