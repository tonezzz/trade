# Archive Retention Policy

This policy defines guidelines for archiving, retaining, and managing historical documentation in the trade project.

## Purpose

The archive retention policy ensures:
- **Historical context**: Valuable historical information is preserved
- **Documentation currency**: Active documentation remains current and relevant
- **Storage efficiency**: Archived content is managed appropriately
- **Compliance**: Retention periods are defined and followed

## Archive Categories

### 1. Documentation Archive (`docs-archive/`)
**Location**: `docs-archive/`

**Purpose**: Historical documentation that is no longer actively maintained but contains valuable context.

**Content Types**:
- Strategy documents from completed phases
- Implementation summaries of completed features
- Historical decision logs
- Project completion summaries
- Outdated planning documents

**Retention Period**: Indefinite (permanent retention)

**Review Frequency**: Annually

**Archiving Criteria**:
- Document is 6+ months old
- Content is historical/superseded
- Contains valuable strategic or implementation context
- No longer actively maintained

**Example Content**:
- `DEV_FEEDBACK_LOOP_ANALYSIS.md`
- `DOCUMENTATION_STRATEGY.md`
- `PROJECT_COMPLETION_SUMMARY.md`

### 2. Workflow Archive (`docs/workflows/archive/`)
**Location**: `docs/workflows/archive/`

**Purpose**: Outdated workflow procedures that may be referenced but are no longer current.

**Content Types**:
- Deprecated operational procedures
- Superseded deployment workflows
- Outdated troubleshooting procedures
- Historical process documentation

**Retention Period**: 2 years

**Review Frequency**: Quarterly

**Archiving Criteria**:
- Workflow is superseded by new procedure
- Process or system has changed significantly
- Workflow is no longer accurate
- May still have historical value

**Disposal Criteria**:
- 2 years since archival
- No longer relevant to any system or process
- No historical value

### 3. Knowledge Archive (`.devin/memory-archive/`)
**Location**: `.devin/memory-archive/`

**Purpose**: Outdated memory entries that are no longer current but may have historical value.

**Content Types**:
- Superseded learnings
- Outdated patterns
- Historical session memory
- Deprecated approaches

**Retention Period**: 1 year

**Review Frequency**: Monthly

**Archiving Criteria**:
- Learning or pattern is superseded
- Approach is no longer valid
- System changes have rendered content obsolete
- May still have historical value

**Disposal Criteria**:
- 1 year since archival
- Completely superseded by current documentation
- No historical or reference value

## Archiving Process

### Step 1: Evaluation
When considering archival, evaluate:
1. **Age**: How old is the content?
2. **Relevance**: Is it still actively used?
3. **Accuracy**: Is the content still accurate?
4. **Value**: Does it have historical or reference value?
5. **Superseded**: Has it been replaced by newer content?

### Step 2: Categorization
Determine the appropriate archive category:
- **Documentation Archive**: For major strategic/historical docs
- **Workflow Archive**: For operational procedures
- **Knowledge Archive**: For memory and learnings

### Step 3: Archive
1. Move content to appropriate archive directory
2. Add archive metadata header:
   ```markdown
   <!-- ARCHIVED: YYYY-MM-DD -->
   <!-- REASON: [archival reason] -->
   <!-- SUPERSEDED_BY: [link to new content if applicable] -->
   ```
3. Update relevant indices to reference archived content
4. Add entry to archive index

### Step 4: Documentation
1. Update archive index with new entry
2. Note archival in CHANGELOG if significant
3. Update any cross-references
4. Consider adding memory entry about archival decision

## Archive Index

Each archive directory should maintain an `ARCHIVE_INDEX.md` file:

```markdown
# Archive Index

## Archived Content

### YYYY-MM-DD - [Document Name]
- **Original Location**: [path]
- **Archived By**: [who]
- **Reason**: [why archived]
- **Superseded By**: [link if applicable]
- **Retention Until**: [disposal date if applicable]

## Statistics
- Total Archived: X
- Archived This Year: Y
- Pending Disposal: Z
```

## Disposal Process

### Step 1: Review
At review frequency, evaluate archived content:
1. Is retention period expired?
2. Does it still have historical value?
3. Is it referenced anywhere?
4. Could it be useful in the future?

### Step 2: Decision
Choose one of:
- **Extend Retention**: Keep for another period
- **Move to Active**: Restore to active documentation
- **Dispose**: Delete permanently

### Step 3: Disposal
If disposal is approved:
1. Remove from archive index
2. Delete the file
3. Update disposal statistics
4. Document disposal in CHANGELOG if significant

## Special Cases

### Legal or Compliance Requirements
If content has legal or compliance implications:
- Retain for required period regardless of other policies
- Mark with compliance tag
- Follow legal hold procedures if required

### High Historical Value
Content with significant historical value:
- Mark as permanent retention
- Consider moving to project history
- Preserve in long-term storage

### Frequently Referenced Archives
If archived content is frequently accessed:
- Consider restoring to active documentation
- Update content if still relevant
- Improve archival categorization

## Maintenance

### Monthly Tasks
- Review knowledge archive for disposal candidates
- Update archive statistics
- Check for broken links to archived content

### Quarterly Tasks
- Review workflow archive for disposal candidates
- Evaluate documentation archive for relevance
- Update archive retention policy if needed

### Annual Tasks
- Comprehensive review of all archives
- Update retention periods if policy changes
- Archive cleanup and optimization

## Responsibilities

### Documentation Maintainer
- Execute archival process
- Maintain archive indices
- Conduct regular reviews
- Update retention policy

### Team Members
- Identify candidates for archival
- Provide context on historical content
- Review disposal recommendations
- Suggest policy improvements

## Policy Review

This retention policy should be reviewed:
- **Annually**: For comprehensive review and updates
- **When needed**: If systems, processes, or requirements change significantly
- **On request**: If team members suggest improvements

## Related Documentation

- [Documentation Index](INDEX.md) - Active documentation
- [Documentation Standards](INDEX.md#documentation-standards) - Documentation maintenance
- [Knowledge Base](knowledge/README.md) - Current knowledge and patterns
- [CHANGELOG](../CHANGELOG.md) - Project changes and history

---

**Policy Version:** 1.0  
**Last Updated:** 2026-08-05
**Next Review:** 2027-08-04  
**Maintainer:** trade documentation team
