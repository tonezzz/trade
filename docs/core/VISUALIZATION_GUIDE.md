
---

**Last Updated:** 2026-08-05
# Price History Visualization Guide

This guide explains how to use the visualization system for the dollar price database.

## Overview

The visualization system uses **Plotly** to create interactive, publication-ready charts for financial time series data. All charts support:

- **Interactive exploration**: Zoom, pan, and hover for detailed data inspection
- **Multiple chart types**: Line charts and OHLCV candlestick charts
- **Automatic styling**: Financial-themed color schemes and layouts
- **Export options**: Save as self-contained HTML files or display interactively

## Installation

The visualization system requires the following dependencies (already included in requirements.txt):

```bash
pip install plotly>=5.18.0 kaleido>=0.2.1
```

## CLI Commands

### 1. Exchange Rate Charts

Plot the price history of a single currency:

```bash
# Basic line chart for EUR over 1 year
python cli.py chart exchange_rates --currency EUR --period 1y

# Candlestick chart for GBP over 6 months
python cli.py chart exchange_rates --currency GBP --period 6m --chart-type candlestick

# Chart with volume subplot
python cli.py chart exchange_rates --currency JPY --period 3m --volume

# Save to HTML file instead of displaying
python cli.py chart exchange_rates --currency EUR --period 1y --output eur_chart.html
```

**Available periods**: `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`

**Chart types**: `line` (default), `candlestick`

### 2. Commodity Price Charts

Plot commodity price history:

```bash
# Gold price over 1 year
python cli.py chart commodity_prices --commodity GOLD --period 1y

# Oil price with candlestick chart
python cli.py chart commodity_prices --commodity OIL --period 6m --chart-type candlestick

# Silver price with volume
python cli.py chart commodity_prices --commodity SILVER --period 3m --volume
```

### 3. Currency Comparison Charts

Compare multiple currencies on the same chart:

```bash
# Compare EUR, GBP, JPY over 3 months (normalized to 100)
python cli.py chart comparison --currencies EUR,GBP,JPY --period 3m

# Compare with raw values (not normalized)
python cli.py chart comparison --currencies EUR,GBP,JPY --period 3m --raw

# Performance comparison (percentage change)
python cli.py chart comparison --currencies EUR,GBP,JPY --period 3m --performance

# Save comparison chart
python cli.py chart comparison --currencies EUR,GBP,JPY --period 6m --output comparison.html
```

### 4. Dollar Index Charts

Plot the Dollar Index (DXY):

```bash
# DXY over 1 year
python cli.py chart dollar_index --period 1y

# DXY with candlestick chart
python cli.py chart dollar_index --period 6m --chart-type candlestick

# DXY with volume
python cli.py chart dollar_index --period 3m --volume
```

## Python API Usage

You can also use the visualization module directly in Python scripts:

```python
from src.database import db
from src.queries import PriceQueries
from src.visualization import get_visualizer

# Get database session and queries
session = db.get_session()
queries = PriceQueries(session)

# Get visualizer
visualizer = get_visualizer(queries)

# Plot exchange rate
fig = visualizer.plot_exchange_rate(
    currency='EUR',
    period='1y',
    chart_type='line',
    show_volume=False
)
fig.show()

# Plot commodity price
fig = visualizer.plot_commodity_price(
    commodity='GOLD',
    period='6m',
    chart_type='candlestick'
)
fig.show()

# Compare currencies
fig = visualizer.plot_currency_comparison(
    currencies=['EUR', 'GBP', 'JPY'],
    period='3m',
    normalize=True
)
fig.show()

# Performance comparison
fig = visualizer.plot_performance_comparison(
    currencies=['EUR', 'GBP', 'JPY'],
    period='3m'
)
fig.show()

# Dollar Index
fig = visualizer.plot_dollar_index(
    period='1y',
    show_volume=True
)
fig.show()

# Save to HTML
fig.write_html('chart.html')

# Close session
session.close()
```

## Chart Features

### Line Charts
- Clean, continuous line showing price over time
- Hover tooltips with exact values
- Automatic color assignment by currency/commodity
- Responsive to zoom and pan

### Candlestick Charts
- Open, High, Low, Close (OHLC) visualization
- Green candles for price increases
- Red candles for price decreases
- Ideal for technical analysis

### Volume Subplots
- Bar chart showing trading volume
- Synchronized with price chart
- Helps identify price-volume relationships

### Comparison Charts
- Multiple currencies on same chart
- Optional normalization (starts at 100)
- Color-coded by currency
- Easy to spot relative performance

### Performance Charts
- Bar chart showing percentage change
- Green for positive, red for negative
- Shows start and end prices on hover
- Quick performance overview

## Color Scheme

The visualization system uses a predefined color palette:

| Currency/Commodity | Color |
|-------------------|-------|
| EUR | Blue (#1f77b4) |
| GBP | Orange (#ff7f0e) |
| JPY | Green (#2ca02c) |
| CHF | Red (#d62728) |
| CAD | Purple (#9467bd) |
| AUD | Brown (#8c564b) |
| GOLD | Gold (#FFD700) |
| SILVER | Silver (#C0C0C0) |
| OIL | Black (#000000) |
| Default | Blue (#007bff) |

## Error Handling

The visualization system includes comprehensive error handling:

- **No data found**: Clear error message if no data exists for the specified currency/commodity and period
- **Invalid period**: Validates period strings and shows valid options
- **Missing OHLC data**: Automatically falls back to line chart if OHLC data is not available
- **Missing volume data**: Gracefully handles missing volume data

## Best Practices

1. **Choose the right chart type**:
   - Use line charts for general trend analysis
   - Use candlestick charts for technical analysis
   - Use volume subplots to identify significant moves

2. **Select appropriate periods**:
   - `1d`, `1w` for intraday analysis
   - `1m`, `3m` for short-term trends
   - `6m`, `1y` for medium-term analysis
   - `5y` for long-term trends

3. **Comparison tips**:
   - Use normalized comparison for relative performance
   - Use raw values for absolute price comparison
   - Use performance charts for quick percentage change overview

4. **Exporting**:
   - Use `--output` to save charts for reports
   - HTML files are self-contained and can be opened in any browser
   - Charts remain interactive in exported HTML

## Examples

### Example 1: Analyze EUR/USD Trend

```bash
# View EUR trend over the past year
python cli.py chart exchange_rates --currency EUR --period 1y

# Check recent volatility with candlestick
python cli.py chart exchange_rates --currency EUR --period 1m --chart-type candlestick --volume
```

### Example 2: Compare Major Currencies

```bash
# Compare EUR, GBP, JPY performance
python cli.py chart comparison --currencies EUR,GBP,JPY --period 3m --performance
```

### Example 3: Gold Price Analysis

```bash
# Gold price over 6 months with volume
python cli.py chart commodity_prices --commodity GOLD --period 6m --volume
```

### Example 4: Dollar Index Analysis

```bash
# DXY with candlestick for technical analysis
python cli.py chart dollar_index --period 6m --chart-type candlestick
```

## Troubleshooting

### Chart doesn't display
- Ensure plotly is installed: `pip install plotly`
- If using CLI, charts open in default browser
- Use `--output` to save as HTML if browser doesn't open

### No data found
- Check that the currency/commodity exists in the database
- Verify the period has data
- Use `python cli.py list currencies` or `python cli.py list commodities` to see available data

### Candlestick chart shows as line
- This means OHLC data is not available
- The system automatically falls back to line chart
- Import data with OHLC fields to enable candlestick charts

## Advanced Usage

### Custom Styling

You can modify the `ChartConfig` class in `src/visualization.py` to customize:

- Color palette
- Chart template
- Default figure size
- Hover templates

### Programmatic Access

The visualization module returns Plotly Figure objects, which can be further customized:

```python
fig = visualizer.plot_exchange_rate('EUR', period='1y')

# Add custom annotations
fig.add_annotation(
    x='2024-01-01',
    y=0.9,
    text='Key Event',
    showarrow=True
)

# Update layout
fig.update_layout(
    title='Custom Title',
    xaxis_rangeslider_visible=False
)

fig.show()
```

## Support

For issues or questions:
1. Check this guide for common solutions
2. Review the test file `test_visualization.py` for examples
3. Examine the source code in `src/visualization.py`
