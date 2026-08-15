#!/bin/bash

# Sync script for TradeCanvas UI deployment
# Development: /home/tony/CascadeProjects/trade/tradecanvas-ui/
# Deployment: /home/tony/CascadeProjects/chaba/stacks/web/public/apps/trade/tradecanvas-ui/

DEV_DIR="/home/tony/CascadeProjects/trade/tradecanvas-ui"
DEPLOY_DIR="/home/tony/CascadeProjects/chaba/stacks/web/public/apps/trade/tradecanvas-ui"

# Files to sync (excluding development-only files)
SYNC_FILES="app.js chart-data-provider.js chart-renderer.js chart-loader.js compare-new.html compare.html compare2.html compare.js favicon.svg hindsight-strategies-new.js hindsight-strategies.js index.html nav.js styles.css strategy-compare-new.js strategy-compare.js strategies-new.js strategies.js test.html test-strategies.html ui-components.js ui-renderer.js"

# Authoritative SSOT source directory
SSOT_DIR="/home/tony/CascadeProjects/trade/config/ssot"

echo "Syncing TradeCanvas UI files..."
echo "From: $DEV_DIR"
echo "To: $DEPLOY_DIR"
echo ""

# Create backup
BACKUP_DIR="/tmp/tradecanvas-ui-backup-$(date +%Y%m%d-%H%M%S)"
echo "Creating backup at $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$DEPLOY_DIR"/* "$BACKUP_DIR/"

# Refresh all UI SSOT files from the authoritative config directory
for ssot_file in "$SSOT_DIR"/ssot.ui.yml "$SSOT_DIR"/ssot.ui.*.yml; do
    if [ -f "$ssot_file" ]; then
        filename=$(basename "$ssot_file")
        echo "Refreshing $filename from $SSOT_DIR"
        cp "$ssot_file" "$DEV_DIR/$filename"
    fi
done

# Sync static UI files
for file in $SYNC_FILES; do
    if [ -f "$DEV_DIR/$file" ]; then
        echo "Syncing: $file"
        cp "$DEV_DIR/$file" "$DEPLOY_DIR/$file"
    else
        echo "Warning: $file not found in development directory"
    fi
done

# Sync all SSOT UI files (picks up new page/family/feature files automatically)
for ssot_file in "$DEV_DIR"/ssot.ui.yml "$DEV_DIR"/ssot.ui.*.yml; do
    if [ -f "$ssot_file" ]; then
        filename=$(basename "$ssot_file")
        echo "Syncing: $filename"
        cp "$ssot_file" "$DEPLOY_DIR/$filename"
    fi
done

# Sync data CSV files
DATA_DIR="/home/tony/CascadeProjects/trade/data/imported"
DATA_DEPLOY_DIR="/home/tony/CascadeProjects/chaba/stacks/web/public/apps/trade/data/imported"

echo ""
echo "Syncing data CSV files..."
mkdir -p "$DATA_DEPLOY_DIR"
for file in "$DATA_DIR"/*_formatted.csv; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "Syncing: $filename"
        sudo cp "$file" "$DATA_DEPLOY_DIR/$filename"
    fi
done

# Fix permissions
echo "Fixing permissions..."
sudo chown -R tony:tony "$DEPLOY_DIR" "$DATA_DEPLOY_DIR"
chmod -R 644 "$DEPLOY_DIR"/*
chmod 755 "$DEPLOY_DIR"
chmod -R 644 "$DATA_DEPLOY_DIR"/*
chmod 755 "$DATA_DEPLOY_DIR"

echo ""
echo "Sync complete!"
echo "Backup available at: $BACKUP_DIR"
echo ""
echo "Testing deployment..."
curl -I http://tony-omen.local:8080/apps/trade/tradecanvas-ui/compare.html
