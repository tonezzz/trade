#!/bin/bash
# Promote a UI feature SSOT from compare2 experimental to stable family/page
# Usage: ./promote-ui-feature.sh <feature-name> <target-file>
# Example: ./promote-ui-feature.sh data-source-selector ssot.ui.compare-family.yml

set -e

FEATURE="$1"
TARGET="$2"

if [ -z "$FEATURE" ] || [ -z "$TARGET" ]; then
    echo "Usage: ./promote-ui-feature.sh <feature-name> <target-file>"
    echo "Example: ./promote-ui-feature.sh data-source-selector ssot.ui.compare-family.yml"
    exit 1
fi

SSOT_DIR="/home/tony/CascadeProjects/trade/config/ssot"
FEATURE_FILE="$SSOT_DIR/ssot.ui.feature.$FEATURE.yml"
TARGET_FILE="$SSOT_DIR/$TARGET"
COMPARE2_FILE="$SSOT_DIR/ssot.ui.compare2.yml"

if [ ! -f "$FEATURE_FILE" ]; then
    echo "ERROR: Feature file not found: $FEATURE_FILE"
    exit 1
fi

if [ ! -f "$TARGET_FILE" ]; then
    echo "ERROR: Target file not found: $TARGET_FILE"
    exit 1
fi

echo "Promoting $FEATURE to $TARGET..."

# Add the feature reference to the target's features list if not already present
# This is a simple append; refine as the merge model evolves
python3 - << EOF
import yaml, sys

target_path = "$TARGET_FILE"
feature_file = "ssot.ui.feature.$FEATURE.yml"

with open(target_path) as f:
    doc = yaml.safe_load(f) or {}

features = doc.get('features', [])
if feature_file not in features:
    features.append(feature_file)
    doc['features'] = features
    with open(target_path, 'w') as f:
        yaml.safe_dump(doc, f, sort_keys=False)
    print(f"Added {feature_file} to {target_path}")
else:
    print(f"{feature_file} already referenced in {target_path}")
EOF

# Remove the feature from compare2's features list if present
python3 - << EOF
import yaml

path = "$COMPARE2_FILE"
with open(path) as f:
    doc = yaml.safe_load(f) or {}

features = doc.get('features', [])
feature_file = "ssot.ui.feature.$FEATURE.yml"
if feature_file in features:
    features.remove(feature_file)
    doc['features'] = features
    with open(path, 'w') as f:
        yaml.safe_dump(doc, f, sort_keys=False)
    print(f"Removed {feature_file} from $COMPARE2_FILE")
EOF

echo "Promotion complete. Run ./sync-tradecanvas-ui.sh to deploy."
