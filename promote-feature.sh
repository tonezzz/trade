#!/bin/bash
# Promote a generic SSOT feature from an experimental/preview target to a stable target.
# Usage: promote-feature.sh <domain> <feature-name> [ssot-dir]
# Example: promote-feature.sh ui data-source-selector
# Example: promote-feature.sh ui data-source-selector /home/tony/CascadeProjects/trade/config/ssot

set -e

DOMAIN="$1"
FEATURE="$2"

if [ -z "$DOMAIN" ] || [ -z "$FEATURE" ]; then
    echo "Usage: promote-feature.sh <domain> <feature-name> [ssot-dir]"
    echo "Example: promote-feature.sh ui data-source-selector"
    echo "Example: promote-feature.sh ui data-source-selector /home/tony/CascadeProjects/trade/config/ssot"
    exit 1
fi

SSOT_DIR="${3:-/home/tony/CascadeProjects/trade/config/ssot}"
FEATURE_FILE="ssot.${DOMAIN}.feature.${FEATURE}.yml"
FEATURE_PATH="$SSOT_DIR/$FEATURE_FILE"

if [ ! -f "$FEATURE_PATH" ]; then
    echo "ERROR: Feature file not found: $FEATURE_PATH"
    exit 1
fi

# Read promote_to and preview_target keys from the feature file
PROMOTE_TO=$(python3 - << EOF
import yaml
with open('$FEATURE_PATH') as f:
    doc = yaml.safe_load(f) or {}
print(doc.get('promote_to', ''))
EOF
)

PREVIEW_TARGET=$(python3 - << EOF
import yaml
with open('$FEATURE_PATH') as f:
    doc = yaml.safe_load(f) or {}
print(doc.get('preview_target', ''))
EOF
)

if [ -z "$PROMOTE_TO" ]; then
    echo "ERROR: $FEATURE_PATH is missing the 'promote_to' key"
    exit 1
fi

TARGET_PATH="$SSOT_DIR/$PROMOTE_TO"
if [ ! -f "$TARGET_PATH" ]; then
    echo "ERROR: Promote target not found: $TARGET_PATH"
    exit 1
fi

echo "Promoting $FEATURE_FILE to $PROMOTE_TO..."

python3 - << EOF
import yaml

target_path = "$TARGET_PATH"
feature_file = "$FEATURE_FILE"

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

if [ -n "$PREVIEW_TARGET" ]; then
    PREVIEW_PATH="$SSOT_DIR/$PREVIEW_TARGET"
    if [ -f "$PREVIEW_PATH" ]; then
        echo "Removing $FEATURE_FILE from $PREVIEW_TARGET..."
        python3 - << EOF
import yaml

path = "$PREVIEW_PATH"
feature_file = "$FEATURE_FILE"

with open(path) as f:
    doc = yaml.safe_load(f) or {}

features = doc.get('features', [])
if feature_file in features:
    features.remove(feature_file)
    doc['features'] = features
    with open(path, 'w') as f:
        yaml.safe_dump(doc, f, sort_keys=False)
    print(f"Removed {feature_file} from {path}")
else:
    print(f"{feature_file} not in {path}, nothing to remove")
EOF
    else
        echo "WARNING: Preview target not found: $PREVIEW_PATH"
    fi
fi

echo "Promotion complete. Remember to:"
echo "  1. Update ssot.index.yml if the feature is new"
echo "  2. Run the relevant sync/deployment script"
