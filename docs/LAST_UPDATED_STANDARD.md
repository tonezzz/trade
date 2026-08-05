# "Last Updated" Field Standardization

This document defines the standard for "Last Updated" fields across all project documentation.

## Standard Format

All documentation files should use the following format for the "Last Updated" field:

```markdown
**Last Updated:** YYYY-MM-DD
```

### Placement

- **Location**: At the end of the document, before any support/contact sections
- **Format**: Bold text with colon, followed by date in ISO 8601 format (YYYY-MM-DD)
- **Example**: `**Last Updated:** 2026-08-04`

## Current Status

As of 2026-08-04, the documentation system has:

- **11 files** using the standard format: `**Last Updated:** 2026-08-04`
- **6 files** using section header format: `## Last Updated`
- **Total**: 17 documentation files with "Last Updated" fields

## Files Needing Standardization

The following files use the section header format and should be updated to the standard format:

1. `docs/core/API_GUIDE.md` - Uses `## Last Updated` section header
2. `docs/core/ARCHITECTURE.md` - Uses `## Last Updated` section header  
3. `docs/knowledge/README.md` - Uses `## Last Updated` section header
4. `docs/knowledge/lessons/lessons-learned.md` - Uses `## Last Updated` section header
5. `docs/workflows/README.md` - Uses `## Last Updated` section header
6. `docs/getting-started/quickstart.md` - Uses `## Last Updated` section header

## Standardization Process

To standardize a file:

1. **Find the "Last Updated" section**:
   ```bash
   grep -n "Last Updated" path/to/file.md
   ```

2. **Replace section header with inline format**:
   ```markdown
   # Before
   ## Last Updated
   
   **Date:** 2026-08-04
   
   # After
   **Last Updated:** 2026-08-04
   ```

3. **Update the date** to the current date if the file was recently modified

## Automation

A script can be created to automate this standardization:

```bash
#!/bin/bash
# Standardize Last Updated fields

find docs/ -name "*.md" -exec sed -i 's/## Last Updated/**Last Updated:**/g' {} +
find docs/ -name "*.md" -exec sed -i '/^## Last Updated$/d' {} +
```

## Maintenance

### When to Update "Last Updated" Fields

Update the "Last Updated" field when:
- Making significant content changes to a document
- Adding new sections or major revisions
- Updating technical information or procedures
- Fixing errors or omissions

### When NOT to Update

Do not update the "Last Updated" field for:
- Minor typo fixes
- Formatting changes only
- Link updates
- Spelling corrections

### Batch Updates

For batch updates across multiple files:
1. Use the standardization script
2. Review changes with `git diff`
3. Commit with message: `docs: standardize Last Updated fields`

## Verification

To verify all "Last Updated" fields are standardized:

```bash
# Check for non-standard formats
grep -r "## Last Updated" docs/

# Should return no results if all are standardized
```

## Related Documentation

- [Documentation Review Schedule](DOCUMENTATION_REVIEW_SCHEDULE.md) - Quarterly review process
- [Documentation Standards](#) - General documentation standards (to be created)
- [CHANGELOG Automation](CHANGELOG_AUTOMATION.md) - Change tracking

---

**Last Updated:** 2026-08-04  
**Maintainer:** trade documentation team