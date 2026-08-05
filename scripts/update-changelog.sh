#!/bin/bash

# CHANGELOG Update Helper Script
# This script helps automate the process of updating CHANGELOG.md
# Usage: ./scripts/update-changelog.sh [type] [description]
# Types: added, changed, deprecated, removed, fixed, security

set -e

CHANGELOG_FILE="CHANGELOG.md"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if CHANGELOG exists
if [ ! -f "$CHANGELOG_FILE" ]; then
    echo "Error: CHANGELOG.md not found in project root"
    exit 1
fi

# Validate arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <type> <description>"
    echo "Types: added, changed, deprecated, removed, fixed, security"
    echo "Example: $0 added 'New feature for user authentication'"
    exit 1
fi

CHANGE_TYPE="$1"
DESCRIPTION="$2"

# Validate change type
case "$CHANGE_TYPE" in
    added|changed|deprecated|removed|fixed|security)
        ;;
    *)
        echo "Error: Invalid change type '$CHANGE_TYPE'"
        echo "Valid types: added, changed, deprecated, removed, fixed, security"
        exit 1
        ;;
esac

# Get current date
TODAY=$(date +%Y-%m-%d)

# Check if [Unreleased] section exists
if ! grep -q "## \[Unreleased\]" "$CHANGELOG_FILE"; then
    echo "Error: [Unreleased] section not found in CHANGELOG.md"
    echo "Please ensure your CHANGELOG.md follows the standard format"
    exit 1
fi

# Check if the subsection exists under [Unreleased]
SUBSECTION="### ${CHANGE_TYPE^}"
if ! grep -A 20 "## \[Unreleased\]" "$CHANGELOG_FILE" | grep -q "$SUBSECTION"; then
    # Subsection doesn't exist, need to add it
    echo "Adding $SUBSECTION subsection to [Unreleased]"
    
    # Find the [Unreleased] section and add subsection after it
    awk -v subsection="$SUBSECTION" -v description="$DESCRIPTION" '
        /^## \[Unreleased\]/ {
            print
            print
            print subsection
            print "- " description
            next
        }
        { print }
    ' "$CHANGELOG_FILE" > "${CHANGELOG_FILE}.tmp"
    
    mv "${CHANGELOG_FILE}.tmp" "$CHANGELOG_FILE"
else
    # Subsection exists, add entry
    echo "Adding entry to existing $SUBSECTION subsection"
    
    # Find the subsection and add entry after it
    awk -v subsection="$SUBSECTION" -v description="$DESCRIPTION" '
        $0 == subsection {
            print
            print "- " description
            in_subsection = 1
            next
        }
        in_subsection && /^### / {
            in_subsection = 0
        }
        { print }
    ' "$CHANGELOG_FILE" > "${CHANGELOG_FILE}.tmp"
    
    mv "${CHANGELOG_FILE}.tmp" "$CHANGELOG_FILE"
fi

echo "✅ CHANGELOG.md updated successfully"
echo "Added: [$CHANGE_TYPE] $DESCRIPTION"
echo ""
echo "Please review the changes and commit them"
