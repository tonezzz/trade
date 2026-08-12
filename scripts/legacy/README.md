# Legacy Download Scripts

This directory contains the original download scripts that have been replaced by the unified data source system.

## Replaced Scripts

The following scripts have been consolidated into the new unified system:

- `download_data.py` → `download_unified.py`
- `download_additional_commodities.py` → `download_unified.py --all --type commodity`
- `download_additional_currencies.py` → `download_unified.py --all --type exchange_rate`
- `download_dxy_data.py` → `download_unified.py --source dxy --symbol DXY`
- `download_thb_data.py` → `download_unified.py --source thb_exchange_rates --symbol THB`
- `download_thai_gold.py` → `download_unified.py --source gold --symbol XAU`
- `download_from_ssot.py` → `download_unified.py --all`

## Migration Guide

### Old Usage
```bash
python download_dxy_data.py
```

### New Usage
```bash
python download_unified.py --source dxy --symbol DXY
```

### List Available Sources
```bash
python download_unified.py --list
```

### Download All Enabled Sources
```bash
python download_unified.py --all
```

## Benefits of New System

- **Unified Interface**: Single script for all data sources
- **Modular Architecture**: Easy to add new data sources
- **Configuration-Driven**: Sources defined in `config/data_sources.yml`
- **Type Safety**: Structured data source classes
- **Error Handling**: Consistent error handling and logging
- **Rate Limiting**: Built-in rate limiting support
- **Extensibility**: Easy to add new data providers

## Legacy Scripts Status

These scripts are kept for reference and backward compatibility. They are no longer maintained and should not be used for new development.

## Next Steps

1. Update any automation scripts to use `download_unified.py`
2. Update scheduler to use the new data source system
3. Remove this directory after confirming all references are updated
