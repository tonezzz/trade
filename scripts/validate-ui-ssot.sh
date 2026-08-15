#!/bin/bash
# Validate TradeCanvas UI SSOT files before sync
# Usage: ./scripts/validate-ui-ssot.sh

set -e

SSOT_DIR="/home/tony/CascadeProjects/trade/config/ssot"

echo "Validating UI SSOT files in $SSOT_DIR..."

# Check all ssot.ui.*.yml files can be parsed
for file in "$SSOT_DIR"/ssot.ui.yml "$SSOT_DIR"/ssot.ui.*.yml; do
    if [ -f "$file" ]; then
        python3 -c "import yaml; yaml.safe_load(open('$file'))" || {
            echo "ERROR: Failed to parse $file"
            exit 1
        }
        echo "OK: $file"
    fi
done

# Check that ref targets are not obviously missing (basic file-level check)
for file in "$SSOT_DIR"/ssot.ui.yml "$SSOT_DIR"/ssot.ui.*.yml; do
    if [ -f "$file" ]; then
        # Find ref: "file#key" or ref: file#key and verify the file part exists
        grep -oP 'ref:\s*"?[^"\n]+\.yml(?:#|\n)' "$file" 2>/dev/null | sed 's/ref://; s/"//g; s/#.*$//' | sort -u | while read -r ref_file; do
            target="$SSOT_DIR/$ref_file"
            if [ ! -f "$target" ]; then
                echo "WARNING: $file references missing file $target"
            fi
        done
    fi
done

echo "SSOT validation complete."
