
---

**Last Updated: 2026-08-04
# Historical Data Sources for Dollar Price Database

This guide provides comprehensive sources for downloading historical dollar price data that can be imported into your database.

## 📊 Exchange Rates (USD to other currencies)

### 1. **HistData.com - Free Forex Historical Data** ⭐ RECOMMENDED
- **URL**: http://www.histdata.com/
- **Coverage**: 66 forex pairs including EUR/USD, GBP/USD, USD/JPY, etc.
- **Format**: CSV files
- **History**: Varies by pair (some going back decades)
- **Cost**: FREE
- **Pairs Available**: EUR/USD, EUR/GBP, EUR/JPY, GBP/USD, USD/JPY, USD/CHF, AUD/USD, NZD/USD, XAU/USD, and many more
- **Download**: Direct download from website

### 2. **European Central Bank (ECB) via Humanitarian Data Exchange**
- **URL**: https://data.humdata.org/dataset/ecb-fx-rates
- **Coverage**: 40+ currencies vs USD
- **Format**: CSV (ECB_FX_USD.csv)
- **History**: 1999-present
- **Cost**: FREE
- **Download**: https://data.humdata.org/dataset/ecb-fx-rates
- **Note**: Daily reference rates from ECB, converted to USD base

### 3. **Federal Reserve (FRED) - St. Louis Fed**
- **URL**: https://fred.stlouisfed.org/
- **Coverage**: Major currencies (EUR, GBP, JPY, CAD, CHF, etc.)
- **Format**: CSV, Excel
- **History**: Varies by series (some 1970s-present)
- **Cost**: FREE
- **Key Series**:
  - EUR/USD: DEXUSEU
  - GBP/USD: DEXUSUK
  - USD/JPY: DEXJPUS
  - USD/CAD: DEXCAUS
- **Download**: https://alfred.stlouisfed.org/series/downloaddata?seid=DEXUSEU

### 4. **DataHub.io - Exchange Rates**
- **URL**: https://datahub.io/core/exchange-rates
- **Coverage**: AUD, EUR, GBP, NZD to USD
- **Format**: CSV (daily, monthly, yearly)
- **History**: 1999-present
- **Cost**: FREE
- **Download**: 
  - Daily: https://datahub.io/core/exchange-rates/_r/-/data/daily.csv
  - Monthly: https://datahub.io/core/exchange-rates/_r/-/data/monthly.csv

### 5. **Kaggle - USD to British Pound Exchange Rate**
- **URL**: https://www.kaggle.com/datasets/jeresalmisto/calcfi-usd-gbp
- **Coverage**: USD/GBP only
- **Format**: CSV
- **History**: 1971-present (daily)
- **Cost**: FREE
- **License**: CC BY 4.0
- **Download**: Requires Kaggle account

## 📈 Dollar Index (DXY)

### 1. **MarketWatch - DXY Download** ⭐ RECOMMENDED
- **URL**: https://www.marketwatch.com/investing/index/dxy/download-data
- **Coverage**: US Dollar Index (DXY)
- **Format**: CSV
- **History**: Several decades
- **Cost**: FREE
- **Data**: OHLCV (Open, High, Low, Close, Volume)
- **Download**: Direct CSV download from website

### 2. **Investing.com - US Dollar Index Historical Data**
- **URL**: https://www.investing.com/currencies/us-dollar-index-historical-data
- **Coverage**: US Dollar Index Futures
- **Format**: CSV (via download button)
- **History**: Available date ranges
- **Cost**: FREE (with account)
- **Data**: Price, Open, High, Low, Volume, Change %
- **Note**: May require account registration

### 3. **Kaggle - US Dollar Index Data (2001-2022)**
- **URL**: https://www.kaggle.com/datasets/balabaskar/us-dollar-index-data
- **Coverage**: US Dollar Index (NYSE)
- **Format**: CSV
- **History**: 2001-2022 YTD
- **Cost**: FREE
- **Data**: OHLC daily data
- **Download**: Requires Kaggle account

### 4. **Barchart.com - U.S. Dollar Index**
- **URL**: https://www.barchart.com/stocks/quotes/%24DXY/historical-download
- **Coverage**: US Dollar Index ($DXY)
- **Format**: CSV
- **History**: Daily data back to 01/01/2000
- **Cost**: FREE tier available (limited downloads)
- **Data**: OHLCV with various timeframes

## 🥇 Commodity Prices

### Gold Prices (XAU/USD)

### 1. **Kaggle - XAUUSD Gold Price Tracker (2004-Present)** ⭐ RECOMMENDED
- **URL**: https://www.kaggle.com/datasets/novandraanugrah/xauusd-gold-price-historical-data-2004present
- **Coverage**: Gold vs USD (XAU/USD)
- **Format**: CSV (multiple timeframes)
- **History**: 2004-present (daily & hourly)
- **Cost**: FREE
- **Data**: OHLCV with multiple timeframes (1m, 5m, 15m, 30m, 1h, 4h, daily)
- **Auto-updated**: Every weekday
- **Download**: Requires Kaggle account

### 2. **Free Gold API - 768 Years of Gold Prices**
- **URL**: https://github.com/olddatasets/gold-spot-downloader
- **Coverage**: Gold spot prices
- **Format**: CSV
- **History**: 1258-2025 (768 years!)
- **Cost**: FREE
- **Data**: Date, Price, Currency
- **Download**: https://freegoldapi.com/data/latest.csv
- **Note**: Amazing historical coverage, data from medieval Britain to modern markets

### 3. **Hugging Face - XAUUSD Gold Price (2004-2025)**
- **URL**: https://huggingface.co/datasets/ZombitX64/xauusd-gold-price-historical-data-2004-2025
- **Coverage**: Gold vs USD
- **Format**: CSV (multiple timeframes)
- **History**: 2004-2025
- **Cost**: FREE
- **Data**: OHLCV with different granularities
- **Download**: Direct download from Hugging Face

### 4. **MarketData Hub - XAU/USD Historical Data**
- **URL**: https://marketdata-hub.com/instrument/xauusd
- **Coverage**: Spot Gold (XAU/USD)
- **Format**: CSV, JSON
- **History**: Daily from 1999-06-03, Tick from 2003-05-05
- **Cost**: FREE tier available
- **Data**: Bid & Ask prices with volume
- **Timeframes**: Tick, 1s, 1m, 5m, 15m, 30m, 1h, 4h, Daily, Monthly
- **Note**: Desktop app for local download

### 5. **Algo Special - Free Forex Historical Data**
- **URL**: https://www.algospecial.com/historical-data/
- **Coverage**: XAU/USD Gold
- **Format**: CSV (2020-2025)
- **History**: 2020-2025
- **Cost**: FREE
- **Data**: All timeframes available
- **Note**: MT4/MT5 backtesting ready

### Crude Oil Prices

### 1. **DataHub.io - Oil Prices** ⭐ RECOMMENDED
- **URL**: https://datahub.io/core/oil-prices
- **Coverage**: Brent and WTI crude oil
- **Format**: CSV (daily, weekly, monthly, yearly)
- **History**: 
  - WTI: January 1986-present
  - Brent: May 1987-present
- **Cost**: FREE
- **Download Links**:
  - WTI Daily: https://datahub.io/core/oil-prices/_r/-/data/wti-daily.csv
  - Brent Daily: https://datahub.io/core/oil-prices/_r/-/data/brent-daily.csv
  - WTI Monthly: https://datahub.io/core/oil-prices/_r/-/data/wti-monthly.csv
  - Brent Monthly: https://datahub.io/core/oil-prices/_r/-/data/brent-monthly.csv

### 2. **Federal Reserve (FRED) - Crude Oil Prices**
- **URL**: https://alfred.stlouisfed.org/
- **Coverage**: WTI and Brent crude oil
- **Format**: CSV, Excel
- **History**: Several decades
- **Cost**: FREE
- **Key Series**:
  - Brent: MCOILBRENTEU
  - WTI: WTISPLC
- **Download**: 
  - Brent: https://alfred.stlouisfed.org/series/downloaddata?seid=MCOILBRENTEU
  - WTI: https://alfred.stlouisfed.org/series/downloaddata?seid=WTISPLC

### 3. **GitHub - Oil Prices Dataset**
- **URL**: https://github.com/datasets/oil-prices
- **Coverage**: Brent and WTI
- **Format**: CSV
- **History**: 1986-present (WTI), 1987-present (Brent)
- **Cost**: FREE
- **Download**: 
  - WTI Daily: https://raw.githubusercontent.com/datasets/oil-prices/main/data/wti-daily.csv
  - Brent Daily: https://raw.githubusercontent.com/datasets/oil-prices/main/data/brent-daily.csv

## 🔄 Quick Start Recommendations

### For Exchange Rates:
1. **Start with ECB data** (comprehensive, free, USD base)
2. **Supplement with FRED data** for specific currencies
3. **Use HistData.com** for forex pair data with OHLCV

### For Dollar Index:
1. **MarketWatch** for easy CSV download with OHLCV
2. **Kaggle dataset** for 2001-2022 period
3. **Investing.com** for recent data and updates

### For Gold Prices:
1. **Free Gold API** for amazing 768-year coverage
2. **Kaggle dataset** for detailed 2004-present OHLCV data
3. **Hugging Face** for alternative 2004-2025 dataset

### For Oil Prices:
1. **DataHub.io** for both WTI and Brent (simple CSV format)
2. **FRED** for official economic data
3. **GitHub datasets** for direct CSV access

## 📥 Import Instructions

### Automated Download Scripts

The project includes automated download scripts for quick data acquisition:

#### Basic Data
```bash
# Download basic historical data (WTI/Brent oil)
python3 download_data.py
```

#### Additional Currency Pairs
```bash
# Download JPY, CAD, CHF, AUD, NZD data
python3 download_additional_currencies.py
```

#### Additional Commodities
```bash
# Download Silver, Copper, Natural Gas, Agricultural commodities
python3 download_additional_commodities.py
```

**Note**: The additional download scripts currently generate sample data for demonstration purposes. For production use, replace the sample data generation with real data sources from the providers listed below.

### Step 1: Download Data
Choose your data source and download the CSV file.

### Step 2: Format the Data
Ensure your CSV matches the template format in `data/templates/`:

**Exchange Rates Template:**
```csv
date,quote_currency,rate,open_price,high_price,low_price,close_price,volume
2024-01-01,EUR,0.9150,0.9145,0.9160,0.9130,0.9155,1000000
```

**Dollar Index Template:**
```csv
date,value,open_price,high_price,low_price,close_price,volume
2024-01-01,101.5,101.3,101.8,101.2,101.6,50000000
```

**Commodity Prices Template:**
```csv
date,commodity,symbol,price,unit,open_price,high_price,low_price,close_price,volume
2024-01-01,GOLD,XAUUSD,2050.50,oz,2048.00,2055.00,2045.00,2052.00,150000
```

### Step 3: Import to Database
```bash
# Using CLI
python cli.py import exchange_rates your_data.csv
python cli.py import dollar_index dxy_data.csv
python cli.py import commodity_prices commodities_data.csv
```

## 🔧 Data Transformation Tips

### Common Format Issues:
1. **Date formats**: Convert to YYYY-MM-DD
2. **Currency codes**: Ensure 3-letter uppercase codes (EUR, GBP, JPY)
3. **Decimal separators**: Use periods (.) not commas (,)
4. **Missing OHLCV**: Set to NULL or leave blank if not available
5. **Base currency**: Most sources provide USD as base, verify this

### Simple Python Conversion Script:
```python
import pandas as pd

# Load downloaded data
df = pd.read_csv('downloaded_data.csv')

# Rename columns to match your template
df = df.rename(columns={
    'Date': 'date',
    'Close': 'rate',  # or 'price' for commodities
    'Currency': 'quote_currency'
})

# Convert date format
df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

# Save in correct format
df.to_csv('formatted_data.csv', index=False)
```

## 📝 License and Attribution

- **ECB Data**: Free to use, cite European Central Bank as source
- **FRED Data**: Public domain, cite Federal Reserve Bank of St. Louis
- **Kaggle Datasets**: Check individual dataset licenses (mostly CC BY)
- **DataHub.io**: Open data, cite datahub.io
- **Free Gold API**: Free with proper attribution

## ⚠️ Important Notes

1. **Data Quality**: Always verify data quality before import
2. **Missing Values**: Handle appropriately (NULL, interpolation, etc.)
3. **Time Zones**: Be aware of time zone differences in data sources
4. **Corporate Actions**: Check for splits, dividends in commodity data
5. **Updates**: Set up regular data update schedules
6. **Backfilling**: Start with recent data and work backwards if needed

## 🚀 Next Steps

1. **Choose your data sources** based on your needs
2. **Download sample data** to test the import process
3. **Set up automated downloads** for regular updates
4. **Validate imported data** using the query functions
5. **Create analysis scripts** for your specific use cases

---

**Happy data hunting!** This database system is designed to handle data from all these sources. Start with the recommended sources and expand as needed.
