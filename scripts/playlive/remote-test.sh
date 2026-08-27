#!/bin/bash
set -euo pipefail

# remote-test.sh
#
# One-button test workflow for PlayLive presets.
# tony-omen only sends one command; all browser, network, and parsing work
# is done on tony-dell.
#
# Usage:
#   scripts/playlive/remote-test.sh [PRESET_REL_PATH] [extra args for runner]
#
# Examples:
#   scripts/playlive/remote-test.sh \
#     config/ssot/ssot.playlive.preset.settrade-market-snapshot.yml
#
#   scripts/playlive/remote-test.sh \
#     config/ssot/ssot.playlive.preset.settrade-symbol-quote.yml \
#     --param symbol=MAJOR

PRESET="${1:-config/ssot/ssot.playlive.preset.settrade-market-snapshot.yml}"
shift || true

HOST="tony-dell"
REMOTE_DIR="/home/tony/CascadeProjects/trade"

# Sync the runner and the chosen preset to tony-dell, preserving paths.
# Send rsync progress to stderr so JSON stays on stdout.
rsync -av --checksum --relative \
  "scripts/playlive/run-preset-against-dell.py" \
  "$PRESET" \
  "$HOST:$REMOTE_DIR/" 1>&2

# Run the preset on tony-dell and stream JSON back to tony-omen.
ssh -o ConnectTimeout=5 "$HOST" \
  "python3 $REMOTE_DIR/scripts/playlive/run-preset-against-dell.py \
    --preset-file '$REMOTE_DIR/$PRESET' \
    -o - \
    $*"
