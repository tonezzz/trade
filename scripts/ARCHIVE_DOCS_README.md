# Archive Documentation Script

**Script:** `archive-docs.sh`  
**Location:** `scripts/archive-docs.sh`  
**Last Updated:** 2026-08-04

## Overview

The `archive-docs.sh` script automates the archival of documentation files that are older than a specified threshold. It helps maintain a clean and organized documentation structure by moving outdated documents to the archive directory while maintaining proper backups and logs.

## Features

- **Automated Archival:** Moves old documentation files to `docs-archive/`
- **Configurable Threshold:** Archive files older than X months (default: 6)
- **Backup Creation:** Creates timestamped backups before archival
- **Index Updates:** Automatically updates `docs/INDEX.md` to remove archived files
- **Archive Logging:** Maintains a log of all archival operations
- **Dry Run Mode:** Preview what would be archived without making changes
- **Safe Operation:** Skips INDEX.md and README.md files to preserve structure

## Usage

### Basic Usage

Archive documentation files older than 6 months (default):

```bash
./scripts/archive-docs.sh
```

### Custom Threshold

Archive files older than 3 months:

```bash
./scripts/archive-docs.sh -m 3
```

### Dry Run

Preview what would be archived without making changes:

```bash
./scripts/archive-docs.sh --dry-run
```

### Custom Backup Directory

Use a custom backup directory:

```bash
./scripts/archive-docs.sh -b /path/to/custom/backup
```

### Help

Display help message:

```bash
./scripts/archive-docs.sh --help
```

## Command Line Options

| Option | Long Option | Description | Default |
|--------|-------------|-------------|---------|
| `-m` | `--months` | Archive docs older than MONTHS | 6 |
| `-d` | `--dry-run` | Show what would be archived without changes | false |
| `-b` | `--backup-dir` | Use custom backup directory | /tmp/trade-docs-backup |
| `-h` | `--help` | Show help message | - |

## How It Works

### 1. Scanning

The script scans the `docs/` directory for Markdown files (`*.md`) that are older than the specified threshold (in months).

### 2. Filtering

The script automatically skips:
- `INDEX.md` files (to preserve navigation structure)
- `README.md` files (to preserve directory documentation)
- Files already in the archive directory

### 3. Backup

Before moving any files, the script:
- Creates a timestamped backup directory
- Copies all files to be archived to the backup
- Maintains the original directory structure

### 4. Archival

The script:
- Creates the same directory structure in `docs-archive/`
- Moves files from `docs/` to `docs-archive/`
- Logs each file move operation

### 5. Index Update

The script:
- Backs up the current `docs/INDEX.md`
- Removes references to archived files from the index
- Preserves the overall structure of the index

### 6. Logging

The script:
- Appends an entry to `docs-archive/archive.log`
- Records timestamp, file count, threshold, and backup location
- Maintains an audit trail of all archival operations

### 7. Cleanup

The script:
- Removes old backups (keeps last 5)
- Prevents backup directory from growing indefinitely

## Archive Log Format

The archive log (`docs-archive/archive.log`) contains entries in the following format:

```
YYYY-MM-DD HH:MM:SS | Archived X files | Threshold: Y months | Backup: /path/to/backup
```

Example:
```
2026-08-04 16:45:30 | Archived 3 files | Threshold: 6 months | Backup: /tmp/trade-docs-backup/backup_20260804_164530
```

## Directory Structure

### Before Archival

```
trade/
├── docs/
│   ├── INDEX.md
│   ├── feature1.md          # Old file
│   ├── feature2.md          # Old file
│   └── feature3.md          # Recent file
└── docs-archive/
    └── archive.log
```

### After Archival

```
trade/
├── docs/
│   ├── INDEX.md            # Updated (old references removed)
│   └── feature3.md          # Recent file (unchanged)
└── docs-archive/
    ├── archive.log         # Updated with new entry
    ├── feature1.md         # Archived
    └── feature2.md         # Archived
```

## Safety Features

### Protected Files

The following files are never archived:
- `INDEX.md` - Documentation navigation
- `README.md` - Directory documentation
- Files in `docs-archive/` - Already archived

### Backup Verification

- Timestamped backups prevent overwriting
- Original directory structure preserved
- Backup location logged for recovery

### Dry Run Mode

Use `--dry-run` to:
- Preview files that would be archived
- Verify threshold settings
- Test script behavior without changes

## Recovery

If you need to recover archived files:

1. **From Backup:**
   ```bash
   # Find the backup from the archive log
   cat docs-archive/archive.log
   
   # Restore from backup
   cp -r /tmp/trade-docs-backup/backup_YYYYMMDD_HHMMSS/* docs/
   ```

2. **From Archive:**
   ```bash
   # Move file back from archive
   mv docs-archive/feature1.md docs/
   
   # Update INDEX.md manually to add reference
   ```

## Best Practices

### Scheduling

Run the archive script regularly:
- **Monthly:** For active projects with frequent documentation updates
- **Quarterly:** For stable projects with occasional updates
- **On-demand:** When documentation reorganization is needed

### Threshold Selection

Choose appropriate thresholds based on project activity:
- **3 months:** Fast-moving projects with rapid iteration
- **6 months:** Standard projects with regular updates (default)
- **12 months:** Stable projects with infrequent changes

### Pre-Archive Review

Before running the script:
1. Review the archive log to understand archival history
2. Use `--dry-run` to preview what will be archived
3. Ensure important files won't be accidentally archived
4. Communicate with team if archival might affect them

### Post-Archive Actions

After running the script:
1. Verify the archive log entry
2. Check that INDEX.md is correctly updated
3. Test that documentation navigation still works
4. Review archived files for any that should be restored

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Archive Documentation

on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly on the 1st

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Archive old docs
        run: ./scripts/archive-docs.sh -m 6
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/ docs-archive/
          git commit -m "Archive documentation older than 6 months" || exit 0
          git push
```

### Cron Job Example

```bash
# Add to crontab (monthly archival)
0 0 1 * * cd /home/tony/CascadeProjects/trade && ./scripts/archive-docs.sh -m 6
```

## Troubleshooting

### Issue: Script Permission Denied

**Solution:**
```bash
chmod +x scripts/archive-docs.sh
```

### Issue: No Files Archived

**Possible causes:**
- Threshold too high (no files old enough)
- All files are protected (INDEX.md, README.md)
- Files already archived

**Solution:**
- Use `--dry-run` to see what would be archived
- Lower the threshold with `-m` option
- Check file modification dates with `ls -la docs/`

### Issue: INDEX.md Not Updated

**Possible causes:**
- INDEX.md not found
- File references don't match exactly

**Solution:**
- Manually update INDEX.md if needed
- Check that archived file names match references
- Restore from backup if needed

### Issue: Backup Directory Full

**Solution:**
- Use custom backup directory with `-b` option
- Manually clean old backups
- Increase disk space for backup location

## Related Documentation

- [Workflow Archival Process](../.windsurf/workflows/ARCHIVAL_PROCESS.md) - General archival process
- [Retention Policy](../.windsurf/workflows/RETENTION_POLICY.md) - Retention guidelines
- [Archive Checklist](../.windsurf/workflows/ARCHIVE_CHECKLIST.md) - Archival checklist
- [Documentation Index](../docs/INDEX.md) - Main documentation index

## Maintenance

- Review script quarterly for effectiveness
- Update threshold based on project needs
- Monitor archive log for patterns
- Adjust backup retention as needed

---

**Last Updated:** 2026-08-04  
**Maintainer:** trade documentation team