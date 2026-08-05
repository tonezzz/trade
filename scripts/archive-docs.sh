#!/bin/bash

################################################################################
# Archive Documentation Script
#
# This script archives documentation files older than a specified age to the
# docs-archive/ directory. It updates the documentation index, maintains an
# archive log, and creates backups before archival.
#
# Usage: ./archive-docs.sh [options]
#
# Options:
#   -m, --months MONTHS    Archive docs older than MONTHS (default: 6)
#   -d, --dry-run          Show what would be archived without making changes
#   -b, --backup-dir DIR   Use custom backup directory (default: /tmp/trade-docs-backup)
#   -h, --help             Show this help message
#
# Examples:
#   ./archive-docs.sh                    # Archive docs older than 6 months
#   ./archive-docs.sh -m 3              # Archive docs older than 3 months
#   ./archive-docs.sh --dry-run          # Preview what would be archived
#
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$PROJECT_ROOT/docs"
ARCHIVE_DIR="$PROJECT_ROOT/docs-archive"
BACKUP_DIR="${BACKUP_DIR:-/tmp/trade-docs-backup}"
ARCHIVE_LOG="$ARCHIVE_DIR/archive.log"
INDEX_FILE="$DOCS_DIR/INDEX.md"
DEFAULT_MONTHS=6

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions

print_usage() {
    grep '^#' "$SCRIPT_DIR/$(basename "$0")" | tail -n +3 | sed 's/^# //; s/^#//'
}

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
MONTHS=$DEFAULT_MONTHS
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--months)
            MONTHS="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -b|--backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Validate inputs
if ! [[ "$MONTHS" =~ ^[0-9]+$ ]]; then
    log_error "Months must be a positive integer"
    exit 1
fi

log "Starting documentation archival process"
log "Project root: $PROJECT_ROOT"
log "Archive threshold: $MONTHS months"
log "Dry run: $DRY_RUN"

# Check directories
if [[ ! -d "$DOCS_DIR" ]]; then
    log_error "Documentation directory not found: $DOCS_DIR"
    exit 1
fi

# Create archive directory if it doesn't exist
if [[ ! -d "$ARCHIVE_DIR" ]]; then
    log "Creating archive directory: $ARCHIVE_DIR"
    if [[ "$DRY_RUN" = false ]]; then
        mkdir -p "$ARCHIVE_DIR"
    fi
fi

# Create backup directory
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CURRENT_BACKUP_DIR="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
if [[ "$DRY_RUN" = false ]]; then
    mkdir -p "$CURRENT_BACKUP_DIR"
    log "Created backup directory: $CURRENT_BACKUP_DIR"
fi

# Find files to archive
log "Scanning for files older than $MONTHS months..."
FILES_TO_ARCHIVE=()

while IFS= read -r -d '' file; do
    # Skip INDEX.md and README.md files
    if [[ "$(basename "$file")" == "INDEX.md" ]] || [[ "$(basename "$file")" == "README.md" ]]; then
        continue
    fi
    
    # Skip files in archive directory
    if [[ "$file" == "$ARCHIVE_DIR"* ]]; then
        continue
    fi
    
    FILES_TO_ARCHIVE+=("$file")
done < <(find "$DOCS_DIR" -type f -name "*.md" -mtime +"$((MONTHS * 30))" -print0)

if [[ ${#FILES_TO_ARCHIVE[@]} -eq 0 ]]; then
    log_success "No files found older than $MONTHS months"
    exit 0
fi

log "Found ${#FILES_TO_ARCHIVE[@]} files to archive"

# Display files to be archived
echo ""
log "Files to be archived:"
for file in "${FILES_TO_ARCHIVE[@]}"; do
    echo "  - $file"
done
echo ""

if [[ "$DRY_RUN" = true ]]; then
    log_warning "Dry run mode - no changes will be made"
    log "Would archive ${#FILES_TO_ARCHIVE[@]} files"
    exit 0
fi

# Create backup
log "Creating backup of files to be archived..."
for file in "${FILES_TO_ARCHIVE[@]}"; do
    relative_path="${file#$DOCS_DIR/}"
    backup_path="$CURRENT_BACKUP_DIR/$relative_path"
    backup_dir=$(dirname "$backup_path")
    mkdir -p "$backup_dir"
    cp "$file" "$backup_path"
done
log_success "Backup created at $CURRENT_BACKUP_DIR"

# Archive files
log "Archiving files..."
ARCHIVED_COUNT=0
for file in "${FILES_TO_ARCHIVE[@]}"; do
    relative_path="${file#$DOCS_DIR/}"
    archive_path="$ARCHIVE_DIR/$relative_path"
    archive_dir=$(dirname "$archive_path")
    
    # Create directory structure in archive
    mkdir -p "$archive_dir"
    
    # Move file to archive
    mv "$file" "$archive_path"
    ((ARCHIVED_COUNT++))
    
    log "Archived: $relative_path"
done

log_success "Archived $ARCHIVED_COUNT files"

# Update INDEX.md
log "Updating documentation index..."
if [[ -f "$INDEX_FILE" ]]; then
    # Create backup of INDEX.md
    cp "$INDEX_FILE" "$CURRENT_BACKUP_DIR/INDEX.md.backup"
    
    # Remove archived file references from INDEX.md
    for file in "${FILES_TO_ARCHIVE[@]}"; do
        filename=$(basename "$file")
        # Remove lines containing the filename
        sed -i.tmp "/$filename/d" "$INDEX_FILE" && rm -f "${INDEX_FILE}.tmp"
    done
    
    log_success "Updated documentation index"
else
    log_warning "INDEX.md not found, skipping index update"
fi

# Update archive log
log "Updating archive log..."
LOG_ENTRY="$(date +'%Y-%m-%d %H:%M:%S') | Archived $ARCHIVED_COUNT files | Threshold: $MONTHS months | Backup: $CURRENT_BACKUP_DIR"
echo "$LOG_ENTRY" >> "$ARCHIVE_LOG"
log_success "Archive log updated"

# Summary
echo ""
log_success "Archival process completed successfully"
echo "Summary:"
echo "  Files archived: $ARCHIVED_COUNT"
echo "  Archive location: $ARCHIVE_DIR"
echo "  Backup location: $CURRENT_BACKUP_DIR"
echo "  Archive log: $ARCHIVE_LOG"
echo ""

# Cleanup old backups (keep last 5)
log "Cleaning up old backups (keeping last 5)..."
ls -t "$BACKUP_DIR" | tail -n +6 | while read -r old_backup; do
    log "Removing old backup: $old_backup"
    rm -rf "$BACKUP_DIR/$old_backup"
done

log_success "Archive script completed"

exit 0