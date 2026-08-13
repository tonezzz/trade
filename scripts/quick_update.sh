#!/bin/bash
# Quick update script for manual data refresh
# Run this when machine comes back online or before going offline

set -e

echo "========================================"
echo "Trade System Quick Update"
echo "========================================"
echo "Started at: $(date '+%Y-%m-%d %H:%M:%S')"

# Check if docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Start Docker first: sudo systemctl start docker"
    exit 1
fi

# Check if trade-api container is running
if ! docker ps | grep -q trade-api; then
    echo "❌ Error: trade-api container is not running"
    echo "Start trade-api first: docker compose up -d trade-api"
    exit 1
fi

echo "✅ Docker and trade-api are running"
echo ""

# Update THB data (most critical)
echo "🔄 Updating THB data..."
docker exec trade-api python scripts/auto_update.py --run-once --job thb_exchange_rates
echo "✅ THB update completed"
echo ""

# Update DXY data
echo "🔄 Updating DXY data..."
docker exec trade-api python scripts/auto_update.py --run-once --job dxy
echo "✅ DXY update completed"
echo ""

# Update commodity data
echo "🔄 Updating commodity data..."
for commodity in copper natural_gas; do
    echo "  Updating $commodity..."
    docker exec trade-api python scripts/auto_update.py --run-once --job $commodity
done
echo "✅ Commodity updates completed"
echo ""

# Update currency data
echo "🔄 Updating currency data..."
for currency in jpy cad chf aud nzd; do
    echo "  Updating $currency..."
    docker exec trade-api python scripts/auto_update.py --run-once --job ${currency}_exchange_rates
done
echo "✅ Currency updates completed"
echo ""

echo "========================================"
echo "Quick update completed"
echo "Finished at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""
echo "Check data quality:"
echo "  curl http://localhost:9000/api/data_quality"
echo ""
echo "Check system health:"
echo "  curl http://localhost:9000/api/health"
