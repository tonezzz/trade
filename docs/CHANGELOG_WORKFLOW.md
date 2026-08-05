# CHANGELOG Workflow

This document describes the procedures and best practices for maintaining the CHANGELOG using the automation tools.

## Overview

The CHANGELOG is maintained using two automation tools:
- **`update-changelog.sh`** - Simple bash script for quick entries
- **`changelog-manager.py`** - Advanced Python tool for validation and releases

## When to Update CHANGELOG

### Mandatory Updates
Update CHANGELOG for:
- All user-facing changes (features, fixes, improvements)
- API changes (endpoints, parameters, behavior)
- Configuration changes that affect users
- Data source changes or additions
- Documentation changes that affect users

### Optional Updates
Consider updating for:
- Internal refactoring (if significant)
- Performance improvements
- Code quality improvements
- Developer tooling changes

### No Update Needed
- Typo fixes in comments
- Minor code clean-up
- Test additions
- Documentation formatting

## CHANGELOG Entry Guidelines

### Change Types

**Added:** New features
```
- New trading signal for RSI calculation
- Support for additional currency pairs
- WebSocket endpoint for real-time data
```

**Changed:** Changes to existing functionality
```
- Improved API response time by optimizing queries
- Updated default configuration values
- Enhanced error messages for better debugging
```

**Deprecated:** Features that will be removed
```
- Legacy CSV import format (use new format)
- Old API endpoint v1 (use v2)
```

**Removed:** Removed features
```
- Removed deprecated data source X
- Removed unused configuration option
```

**Fixed:** Bug fixes
```
- Fixed database connection timeout issue
- Fixed incorrect calculation in moving average
- Fixed WebSocket reconnection logic
```

**Security:** Security improvements
```
- Added input validation to prevent SQL injection
- Updated dependencies for security patches
- Improved API authentication
```

### Writing Good Entries

**DO:**
- Focus on user impact, not implementation details
- Be specific and descriptive
- Use active voice
- Group related changes together
- Mention what changed, not how

**DON'T:**
- Include technical implementation details
- Use vague language like "improvements"
- Write paragraphs (keep it concise)
- Include internal code references
- Mention commit hashes or PR numbers

**Examples:**

❌ Bad:
```
- Fixed bug in the database query function where the date parameter wasn't being properly escaped, causing SQL errors
- Refactored the API layer to use dependency injection for better testability
- Updated the configuration file structure to use YAML instead of JSON
```

✅ Good:
```
- Fixed database query parameter validation
- Improved API testability with dependency injection
- Migrated configuration format from JSON to YAML
```

## Daily CHANGELOG Workflow

### During Development

**For Small Changes:**
```bash
# Quick entry for a single change
./scripts/update-changelog.sh added "New feature description"
./scripts/update-changelog.sh fixed "Bug fix description"
```

**For Multiple Related Changes:**
```bash
# Add each change individually
./scripts/update-changelog.sh added "Feature part 1"
./scripts/update-changelog.sh added "Feature part 2"
./scripts/update-changelog.sh changed "Related improvement"
```

**For Complex Changes:**
```bash
# Use the advanced tool for more control
python3 scripts/changelog-manager.py add added "Complex feature description"
```

### Before Committing

**Pre-Commit Checklist:**
- [ ] CHANGELOG updated for all user-facing changes
- [ ] Entries use appropriate change types
- [ ] Entries are descriptive and user-focused
- [ ] Related changes grouped together
- [ ] No implementation details in entries

**Validation:**
```bash
# Validate CHANGELOG format
python3 scripts/changelog-manager.py validate
```

### Commit Message Integration

**Option 1: Separate CHANGELOG Commit**
```bash
# Commit code changes
git add src/
git commit -m "feat: implement new trading signal"

# Update CHANGELOG
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for new trading signal"
```

**Option 2: Combined Commit**
```bash
# Commit everything together
git add src/ CHANGELOG.md
git commit -m "feat: implement new trading signal

- Added RSI signal calculation
- Updated configuration
- Updated CHANGELOG"
```

## Release Workflow

### Pre-Release Preparation

**1. Review Unreleased Entries:**
```bash
# View current CHANGELOG
cat CHANGELOG.md

# Ensure all changes are documented
# Verify entries are descriptive and accurate
# Check that change types are appropriate
```

**2. Validate Format:**
```bash
python3 scripts/changelog-manager.py validate
```

**3. Review Completeness:**
- Are all user-facing changes documented?
- Are entries descriptive and user-focused?
- Is the version number appropriate?
- Is the release date correct?

### Creating a Release

**1. Update Version Number:**
Determine appropriate version based on changes:
- **Major (X.0.0)**: Breaking changes, major architectural changes
- **Minor (0.X.0)**: New features, significant enhancements
- **Patch (0.0.X)**: Bug fixes, minor improvements, documentation updates

**2. Create Release:**
```bash
# Create release from Unreleased entries
python3 scripts/changelog-manager.py release 1.2.3

# Or with specific date
python3 scripts/changelog-manager.py release 1.2.3 --date 2026-08-04
```

**3. Tag the Release:**
```bash
# Create annotated tag
git tag -a v1.2.3 -m "Release version 1.2.3

- Added new trading signals
- Improved API performance
- Fixed database connection issues"

# Push tag to remote
git push origin v1.2.3
```

**4. Update Documentation:**
- Update version numbers in documentation
- Update "Last Updated" fields
- Announce release to team

## CHANGELOG Automation Best Practices

### Tool Selection

**Use `update-changelog.sh` for:**
- Quick, daily entries during development
- Simple, straightforward changes
- When you're comfortable with bash scripts
- Routine change documentation

**Use `changelog-manager.py` for:**
- Pre-release validation
- Complex changelog operations
- Version releases
- When you need advanced features
- Format validation

### Integration with Git Hooks (Optional)

**Pre-Commit Hook (Optional):**
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Check if CHANGELOG was modified
if git diff --cached --name-only | grep -q "CHANGELOG.md"; then
    # Validate CHANGELOG format
    python3 scripts/changelog-manager.py validate
    if [ $? -ne 0 ]; then
        echo "ERROR: CHANGELOG validation failed"
        exit 1
    fi
fi
```

**Pre-Push Hook (Optional):**
```bash
# .git/hooks/pre-push
#!/bin/bash
# Check if there are changes without CHANGELOG updates
CHANGED_FILES=$(git diff --name-only origin/main)
if echo "$CHANGED_FILES" | grep -q "src/"; then
    if ! git diff --name-only origin/main | grep -q "CHANGELOG.md"; then
        echo "WARNING: Source code changes without CHANGELOG updates"
        echo "Consider updating CHANGELOG.md before pushing"
    fi
fi
```

### Team Guidelines

**For Individual Developers:**
- Update CHANGELOG as you complete changes
- Be descriptive and user-focused
- Validate format before committing
- Ask for help if unsure about change type

**For Code Reviewers:**
- Check CHANGELOG is updated for user-facing changes
- Verify entries are descriptive and accurate
- Ensure appropriate change types are used
- Validate CHANGELOG format during review

**For Maintainers:**
- Review CHANGELOG during release preparation
- Ensure consistency across entries
- Validate format before creating releases
- Archive old releases appropriately

## Troubleshooting

### Validation Fails

**Missing Subsections:**
```bash
# ERROR: Missing '### Deprecated' in [Unreleased]
# Solution: Add empty subsections to CHANGELOG.md

## [Unreleased]

### Added
- Your entries here

### Changed
- Your entries here

### Deprecated

### Removed

### Fixed

### Security
```

**Invalid Version Format:**
```bash
# ERROR: Invalid version format: 1.2
# Solution: Use semantic versioning: 1.2.3
```

### Script Errors

**Permission Denied:**
```bash
# bash: ./scripts/update-changelog.sh: Permission denied
# Solution: Make script executable
chmod +x scripts/update-changelog.sh
chmod +x scripts/changelog-manager.py
```

**Python Not Found:**
```bash
# python3: command not found
# Solution: Use python instead or install python3
python scripts/changelog-manager.py validate
```

### Entry Issues

**Entry Not Appearing:**
- Check if you're in the project root directory
- Verify CHANGELOG.md exists
- Check file permissions
- Run with verbose output if available

**Wrong Subsection:**
- Manually edit CHANGELOG.md to move entry
- Or use changelog-manager.py to add to correct section

## CHANGELOG Maintenance

### Monthly
- Review Unreleased entries for completeness
- Clean up any incomplete or vague entries
- Ensure all user-facing changes are documented

### Quarterly
- Review CHANGELOG format consistency
- Archive old releases if needed
- Update this workflow document based on team feedback
- Review tool usage and effectiveness

### Annually
- Comprehensive CHANGELOG review
- Evaluate tool effectiveness
- Consider automation improvements
- Update workflow based on lessons learned

## Examples

### Feature Development
```bash
# Implement feature
# ... development work ...

# Update CHANGELOG
./scripts/update-changelog.sh added "New RSI trading signal with configurable parameters"
./scripts/update-changelog.sh changed "Updated signal configuration schema"

# Commit
git add src/ CHANGELOG.md
git commit -m "feat: add RSI trading signal"
```

### Bug Fix
```bash
# Fix bug
# ... bug fix work ...

# Update CHANGELOG
./scripts/update-changelog.sh fixed "Fixed incorrect calculation in Bollinger Bands"

# Commit
git add src/ CHANGELOG.md
git commit -m "fix: correct Bollinger Bands calculation"
```

### Release
```bash
# Review Unreleased entries
cat CHANGELOG.md

# Validate
python3 scripts/changelog-manager.py validate

# Create release
python3 scripts/changelog-manager.py release 1.2.3

# Tag
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

## Related Documentation

- [CHANGELOG](../CHANGELOG.md) - The actual changelog
- [Development Workflow](DEVELOPMENT_WORKFLOW.md) - Overall development process
- [Scripts Documentation](../scripts/README.md) - Tool documentation
- [Semantic Versioning](https://semver.org/) - Versioning specification
- [Keep a Changelog](https://keepachangelog.com/) - Changelog format

---

**Last Updated:** 2026-08-04
**Workflow Version:** 1.0
**Maintainer:** trade development team
