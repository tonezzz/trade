# Archive Management Procedures

This document provides operational procedures for implementing the archive retention policy across the trade project's documentation systems.

## Overview

Archive management ensures that:
- Historical content is preserved appropriately
- Active documentation remains current
- Storage is used efficiently
- Retention policies are followed consistently

## Archive Categories

### 1. Documentation Archive (`docs-archive/`)
**Retention**: Permanent (indefinite)
**Review Frequency**: Annually
**Content**: Historical strategic documents, implementation summaries, project completion records

### 2. Workflow Archive (`docs/workflows/archive/`)
**Retention**: 2 years
**Review Frequency**: Quarterly
**Content**: Deprecated operational procedures, superseded workflows

### 3. Knowledge Archive (`.devin/memory-archive/`)
**Retention**: 1 year
**Review Frequency**: Monthly
**Content**: Superseded learnings, outdated patterns, historical session memory

## Archiving Procedures

### Documentation Archive Procedure

**When to Archive:**
- Document is 6+ months old
- Content is historical or superseded
- Contains valuable strategic context
- No longer actively maintained

**Archiving Process:**

1. **Evaluation**
   ```bash
   # Review document for archival criteria
   # Check age, relevance, accuracy, value
   ```

2. **Preparation**
   ```bash
   # Add archive metadata header to document
   <!-- ARCHIVED: YYYY-MM-DD -->
   <!-- REASON: [archival reason] -->
   <!-- SUPERSEDED_BY: [link to new content if applicable] -->
   ```

3. **Archival**
   ```bash
   # Move to docs-archive/
   mv docs/old-document.md docs-archive/old-document.md
   ```

4. **Documentation**
   ```bash
   # Update docs-archive/ARCHIVE_INDEX.md
   # Add entry with metadata
   ```

5. **Cross-Reference Update**
   ```bash
   # Update docs/INDEX.md to reference archived content
   # Update any cross-references in active docs
   ```

**Example:**
```markdown
## 2026-08-04 - Original Documentation Strategy
- **Original Location**: docs/DOCUMENTATION_STRATEGY.md
- **Archived By**: Documentation system improvements
- **Reason**: Superseded by new documentation system with portal and knowledge base
- **Superseded By**: docs/PORTAL.md, docs/DEVELOPMENT_WORKFLOW.md
- **Retention**: Permanent (historical value)
```

### Workflow Archive Procedure

**When to Archive:**
- Workflow is superseded by new procedure
- Process or system has changed significantly
- Workflow is no longer accurate
- May still have historical value

**Archiving Process:**

1. **Evaluation**
   ```bash
   # Review workflow for archival criteria
   # Check if superseded, still accurate, historical value
   ```

2. **Preparation**
   ```bash
   # Add archive metadata
   <!-- ARCHIVED: YYYY-MM-DD -->
   <!-- REASON: [archival reason] -->
   <!-- SUPERSEDED_BY: [link to new workflow] -->
   <!-- RETENTION_UNTIL: YYYY-MM-DD -->
   ```

3. **Archival**
   ```bash
   # Create archive directory if needed
   mkdir -p docs/workflows/archive
   
   # Move to archive
   mv docs/workflows/old-workflow.md docs/workflows/archive/old-workflow.md
   ```

4. **Documentation**
   ```bash
   # Update workflow archive index
   # Update docs/workflows/README.md
   ```

**Example Entry:**
```markdown
## Archived Workflows

### 2026-08-04 - Legacy Deployment Workflow
- **Original**: docs/workflows/deployment-legacy.md
- **Archived By**: System update
- **Reason**: Superseded by new deployment procedure
- **Superseded By**: docs/workflows/deployment.md
- **Retention Until**: 2028-08-04
```

### Knowledge Archive Procedure

**When to Archive:**
- Learning or pattern is superseded
- Approach is no longer valid
- System changes have rendered content obsolete
- May still have historical value

**Archiving Process:**

1. **Evaluation**
   ```bash
   # Review memory entry for archival criteria
   # Check if superseded, still valid, historical value
   ```

2. **Preparation**
   ```bash
   # Add archive metadata
   <!-- ARCHIVED: YYYY-MM-DD -->
   <!-- REASON: [archival reason] -->
   <!-- SUPERSEDED_BY: [link to new content] -->
   <!-- RETENTION_UNTIL: YYYY-MM-DD -->
   ```

3. **Archival**
   ```bash
   # Create archive directory if needed
   mkdir -p .devin/memory-archive/{sessions,learnings,patterns}
   
   # Move to appropriate archive
   mv .devin/memory/learnings/old-learning.md .devin/memory-archive/learnings/old-learning.md
   ```

4. **Documentation**
   ```bash
   # Update memory archive index
   # Update .devin/memory/ category READMEs
   ```

## Review Procedures

### Documentation Archive Review (Annual)

**Review Process:**

1. **Preparation** (30 minutes)
   ```bash
   # List all archived content
   ls -la docs-archive/
   
   # Review archive index
   cat docs-archive/ARCHIVE_INDEX.md
   ```

2. **Content Review** (60 minutes)
   ```bash
   # For each archived document:
   # - Assess historical value
   # - Check if still relevant
   # - Verify retention is appropriate
   ```

3. **Decision Making** (30 minutes)
   For each document, choose:
   - **Keep**: Continue permanent retention
   - **Move to Active**: Restore to active documentation
   - **Special Handling**: Mark for legal/compliance hold

4. **Documentation** (30 minutes)
   ```bash
   # Update archive index with review findings
   # Document any decisions made
   # Update retention policy if needed
   ```

**Review Template:**
```markdown
## Documentation Archive Review - [Year]

### Reviewed Content
- Total documents: [count]
- Reviewed this year: [count]
- Historical value confirmed: [count]

### Decisions
- Continue permanent retention: [list]
- Restore to active: [list]
- Special handling: [list]

### Policy Updates
- [ ] Retention policy changes needed
- [ ] Archive procedure improvements
- [ ] Index updates needed
```

### Workflow Archive Review (Quarterly)

**Review Process:**

1. **Preparation** (15 minutes)
   ```bash
   # List archived workflows
   ls -la docs/workflows/archive/
   
   # Check retention dates
   grep "RETENTION_UNTIL" docs/workflows/archive/*.md
   ```

2. **Disposal Check** (30 minutes)
   ```bash
   # Identify workflows past retention date
   # For each, evaluate:
   # - Is retention period expired?
   # - Does it still have historical value?
   # - Is it referenced anywhere?
   ```

3. **Decision Making** (30 minutes)
   For each workflow past retention:
   - **Extend Retention**: Keep for another period
   - **Move to Active**: Restore to active documentation
   - **Dispose**: Delete permanently

4. **Execution** (15 minutes)
   ```bash
   # Execute disposal decisions
   # Update archive index
   # Document disposal in CHANGELOG if significant
   ```

**Review Template:**
```markdown
## Workflow Archive Review - [Quarter]

### Disposal Candidates
- Past retention date: [count]
- Historical value: [count]
- Referenced elsewhere: [count]

### Decisions
- Extend retention: [list]
- Restore to active: [list]
- Dispose: [list]

### Disposal Executed
- Files deleted: [list]
- Index updated: [yes/no]
- CHANGELOG updated: [yes/no]
```

### Knowledge Archive Review (Monthly)

**Review Process:**

1. **Preparation** (10 minutes)
   ```bash
   # List archived memory entries
   ls -la .devin/memory-archive/
   
   # Check retention dates
   grep "RETENTION_UNTIL" .devin/memory-archive/*/*.md
   ```

2. **Disposal Check** (20 minutes)
   ```bash
   # Identify entries past retention date
   # For each, evaluate:
   # - Is retention period expired?
   # - Does it still have historical value?
   # - Could it be useful in the future?
   ```

3. **Decision Making** (20 minutes)
   For each entry past retention:
   - **Extend Retention**: Keep for another period
   - **Move to Active**: Restore to active memory
   - **Dispose**: Delete permanently

4. **Execution** (10 minutes)
   ```bash
   # Execute disposal decisions
   # Update memory archive index
   # Update category indices
   ```

**Review Template:**
```markdown
## Knowledge Archive Review - [Month]

### Disposal Candidates
- Past retention date: [count]
- Historical value: [count]
- Potential future use: [count]

### Decisions
- Extend retention: [list]
- Restore to active: [list]
- Dispose: [list]

### Statistics
- Total archived: [count]
- Disposed this month: [count]
- Extended retention: [count]
```

## Disposal Procedures

### Pre-Disposal Checklist

Before disposing of any archived content:
- [ ] Retention period has expired
- [ ] No historical value identified
- [ ] Not referenced in active documentation
- [ ] No legal or compliance requirements
- [ ] Not marked for special handling
- [ ] Disposal documented in archive index

### Disposal Execution

**For Documentation Archive:**
```bash
# Rare - most documentation archive is permanent
# Only dispose if absolutely no value and not legally required

# Document disposal
echo "## YYYY-MM-DD - [Document Name]" >> docs-archive/ARCHIVE_INDEX.md
echo "- **Disposed**: YYYY-MM-DD" >> docs-archive/ARCHIVE_INDEX.md
echo "- **Reason**: [disposal reason]" >> docs-archive/ARCHIVE_INDEX.md

# Delete file
rm docs-archive/document.md
```

**For Workflow Archive:**
```bash
# Document disposal in workflow archive index
echo "## YYYY-MM-DD - [Workflow Name]" >> docs/workflows/archive/ARCHIVE_INDEX.md
echo "- **Disposed**: YYYY-MM-DD" >> docs/workflows/archive/ARCHIVE_INDEX.md
echo "- **Reason**: Retention expired, no historical value" >> docs/workflows/archive/ARCHIVE_INDEX.md

# Delete file
rm docs/workflows/archive/workflow.md
```

**For Knowledge Archive:**
```bash
# Document disposal in memory archive index
echo "## YYYY-MM-DD - [Memory Entry]" >> .devin/memory-archive/ARCHIVE_INDEX.md
echo "- **Disposed**: YYYY-MM-DD" >> .devin/memory-archive/ARCHIVE_INDEX.md
echo "- **Reason**: Retention expired, superseded by current documentation" >> .devin/memory-archive/ARCHIVE_INDEX.md

# Delete file
rm .devin/memory-archive/learnings/entry.md
```

## Restoration Procedures

### When to Restore Archived Content

- Content is needed for active reference
- Historical context is required for current work
- Content was archived in error
- New use case for archived content discovered

### Restoration Process

**From Documentation Archive:**
```bash
# Evaluate current relevance
# Update content if needed
# Move to active location
mv docs-archive/document.md docs/document.md

# Update documentation indices
# Remove from archive index
# Add to active documentation index
```

**From Workflow Archive:**
```bash
# Evaluate current accuracy
# Update procedure if needed
# Move to active location
mv docs/workflows/archive/workflow.md docs/workflows/workflow.md

# Update workflow index
# Remove from archive index
# Test procedure for accuracy
```

**From Knowledge Archive:**
```bash
# Evaluate current validity
# Update content if needed
# Move to active location
mv .devin/memory-archive/learnings/entry.md .devin/memory/learnings/entry.md

# Update memory indices
# Remove from archive index
# Update category README
```

## Archive Index Management

### Documentation Archive Index

**Location:** `docs-archive/ARCHIVE_INDEX.md`

**Maintain:**
- Complete list of archived documents
- Archival metadata (date, reason, superseded by)
- Retention information
- Disposal records

**Update When:**
- Content is archived
- Content is restored
- Content is disposed
- Annual review completed

### Workflow Archive Index

**Location:** `docs/workflows/archive/ARCHIVE_INDEX.md`

**Maintain:**
- List of archived workflows
- Retention dates
- Disposal records
- Restoration records

**Update When:**
- Workflow is archived
- Workflow is restored
- Workflow is disposed
- Quarterly review completed

### Knowledge Archive Index

**Location:** `.devin/memory-archive/ARCHIVE_INDEX.md`

**Maintain:**
- List of archived memory entries
- Retention dates
- Disposal records
- Category breakdown

**Update When:**
- Memory entry is archived
- Entry is restored
- Entry is disposed
- Monthly review completed

## Automation Opportunities

### Archive Automation Scripts

**Archive Helper Script:**
```bash
#!/bin/bash
# scripts/archive-helper.sh

# Add archive metadata to file
# Move to appropriate archive location
# Update archive index
# Log archival action
```

**Review Automation:**
```bash
#!/bin/bash
# scripts/archive-review.sh

# Check retention dates
# Identify disposal candidates
# Generate review report
# Suggest actions
```

**Index Management:**
```bash
#!/bin/bash
# scripts/update-archive-index.sh

# Scan archive directories
# Update indices automatically
# Generate statistics
# Validate index consistency
```

## Troubleshooting

### Archive Issues

**Content Archived in Error:**
- Use restoration procedures
- Document error in archive index
- Review archival criteria to prevent recurrence

**Lost Archive Metadata:**
- Reconstruct from git history if available
- Document best-guess metadata
- Add note about missing metadata in index

**Broken Links to Archived Content:**
- Update cross-references in active docs
- Add note about archival in active docs
- Consider restoration if frequently accessed

### Review Issues

**Missed Review Schedule:**
- Conduct review as soon as possible
- Document reason for delay
- Adjust schedule if needed
- Consider automation reminders

**Disposal Decisions Unclear:**
- Err on side of retention
- Consult with team if uncertain
- Document uncertainty in index
- Extend retention and review again next period

## Related Documentation

- [Archive Retention Policy](ARCHIVE_RETENTION_POLICY.md) - Retention guidelines
- [Documentation Review Schedule](DOCUMENTATION_REVIEW_SCHEDULE.md) - Review procedures
- [Knowledge Capture Guidelines](KNOWLEDGE_CAPTURE_GUIDELINES.md) - Capture procedures
- [Development Workflow](DEVELOPMENT_WORKFLOW.md) - Development process

---

**Last Updated:** 2026-08-04
**Procedures Version:** 1.0
**Maintainer:** trade documentation team
**Next Scheduled Review:** 2026-11-04 (Quarterly Workflow Archive Review)
