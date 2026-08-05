#!/bin/bash

# Documentation Date Update Script
# This script automatically updates or adds "Last Updated" fields to all markdown files
# in the docs/ directory based on file modification time.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCS_DIR="docs"
DATE_FORMAT="%Y-%m-%d"
LAST_UPDATED_PATTERN="Last Updated:"
DRY_RUN=false

# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --dir DIR       Documentation directory (default: docs/)"
    echo "  -n, --dry-run       Show changes without modifying files"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Update all docs in docs/"
    echo "  $0 -d docs-archive  # Update docs in docs-archive/"
    echo "  $0 -n               # Dry run to see what would change"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dir)
            DOCS_DIR="$2"
            shift 2
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            ;;
    esac
done

# Check if docs directory exists
if [ ! -d "$DOCS_DIR" ]; then
    echo -e "${RED}Error: Directory '$DOCS_DIR' not found${NC}"
    exit 1
fi

# Function to get file modification date
get_file_date() {
    local file="$1"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        stat -f "%Sm" -t "$DATE_FORMAT" "$file"
    else
        # Linux
        date -r "$file" +"$DATE_FORMAT"
    fi
}

# Function to update or add last updated field
update_file_date() {
    local file="$1"
    local new_date=$(get_file_date "$file")
    local temp_file=$(mktemp)
    local updated=false

    # Check if file already has Last Updated field
    if grep -q "$LAST_UPDATED_PATTERN" "$file"; then
        # Update existing Last Updated field
        if sed "s/.*$LAST_UPDATED_PATTERN.*/**Last Updated:** $new_date/" "$file" > "$temp_file"; then
            if ! diff -q "$file" "$temp_file" > /dev/null 2>&1; then
                updated=true
            fi
        fi
    else
        # Add Last Updated field at the end of file
        if echo "" >> "$temp_file" && echo "---" >> "$temp_file" && echo "" >> "$temp_file" && echo "**Last Updated:** $new_date" >> "$temp_file"; then
            cat "$file" >> "$temp_file"
            updated=true
        fi
    fi

    if [ "$updated" = true ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${BLUE}[DRY RUN]${NC} Would update: $file"
            echo -e "  New date: $new_date"
        else
            mv "$temp_file" "$file"
            echo -e "${GREEN}✓ Updated:${NC} $file"
            echo -e "  Date: $new_date"
        fi
        return 0
    else
        rm -f "$temp_file"
        return 1
    fi
}

# Main execution
echo -e "${BLUE}=== Documentation Date Update Script ===${NC}"
echo -e "Directory: $DOCS_DIR"
echo -e "Date format: $DATE_FORMAT"
echo -e "Dry run: $DRY_RUN"
echo ""

# Counters
total_files=0
updated_files=0
skipped_files=0

# Find all markdown files in the directory
while IFS= read -r -d '' file; do
    ((total_files++))
    
    if update_file_date "$file"; then
        ((updated_files++))
    else
        ((skipped_files++))
    fi
done < <(find "$DOCS_DIR" -name "*.md" -print0)

# Also check root-level markdown files
for file in *.md; do
    if [ -f "$file" ]; then
        ((total_files++))
        
        if update_file_date "$file"; then
            ((updated_files++))
        else
            ((skipped_files++))
        fi
    fi
done

# Summary
echo ""
echo -e "${BLUE}=== Summary ===${NC}"
echo -e "Total files scanned: $total_files"
echo -e "${GREEN}Files updated: $updated_files${NC}"
echo -e "${YELLOW}Files skipped (no change needed): $skipped_files${NC}"

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo -e "${YELLOW}This was a dry run. No files were modified.${NC}"
    echo -e "Run without -n flag to apply changes."
fi

exit 0