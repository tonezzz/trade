# Development Workflow

This document describes the integrated development workflow for the trade project, incorporating the new documentation systems (CHANGELOG, knowledge base, workflows, memory capture) into daily development practices.

## Overview

The development workflow follows these phases:
1. **Planning** - Define task and approach
2. **Development** - Implement changes
3. **Documentation** - Update docs and capture knowledge
4. **Verification** - Test and validate
5. **Integration** - Merge and release

## Phase 1: Planning

### 1.1 Task Definition
- Clearly define what needs to be done
- Identify affected components and documentation
- Check for existing patterns in knowledge base
- Review relevant workflows

### 1.2 Research
- Use `subagent_explore` for codebase investigation if needed
- Consult knowledge base for relevant patterns and learnings
- Review existing documentation for context
- Check CHANGELOG for recent related changes

### 1.3 Approach Planning
- Plan implementation approach based on existing patterns
- Identify documentation updates needed
- Determine if new workflow procedures are needed
- Plan knowledge capture opportunities

## Phase 2: Development

### 2.1 Implementation
- Follow existing code patterns (see knowledge base)
- Make changes incrementally
- Test as you go
- Document any deviations from patterns

### 2.2 CHANGELOG Updates
**During Development:**
```bash
# Quick updates for small changes
./scripts/update-changelog.sh added "Feature description"
./scripts/update-changelog.sh fixed "Bug fix description"

# Or use the advanced tool
python3 scripts/changelog-manager.py add added "Feature description"
```

**Best Practices:**
- Update CHANGELOG as you complete each significant change
- Be descriptive about user impact, not implementation details
- Use appropriate change types (added, changed, fixed, etc.)
- Group related changes together

### 2.3 Documentation Updates
- Update relevant documentation files
- Add cross-references to related docs
- Update "Last Updated" fields
- Consider if content belongs in knowledge base

## Phase 3: Documentation & Knowledge Capture

### 3.1 Documentation Updates
**Standard Documentation:**
- Update feature docs for user-facing changes
- Update API docs for API changes
- Update troubleshooting docs for common issues
- Update architecture docs for structural changes

**Documentation Standards:**
- Follow existing format and structure
- Include examples where helpful
- Add troubleshooting sections
- Cross-reference related documentation

### 3.2 Knowledge Capture
**When to Add to Knowledge Base:**
- Discovering a reusable pattern or approach
- Learning something that could help future work
- Solving a complex problem with a good solution
- Identifying best practices or anti-patterns

**Knowledge Article Creation:**
```bash
# Create knowledge article using template
cd docs/knowledge/[category]
# Use the template from the category README
vim your-new-article.md
```

**Update Category Index:**
- Add your article to the category README
- Include brief description
- Add relevant tags

### 3.3 Workflow Documentation
**When to Create Workflows:**
- Documenting a repeatable multi-step process
- Creating procedures for operational tasks
- Capturing troubleshooting methodologies
- Standardizing deployment or maintenance procedures

**Workflow Creation:**
```bash
# Create workflow using template
cd docs/workflows
vim your-new-workflow.md
```

**Update Workflow Index:**
- Add to appropriate category in workflows/README.md
- Include complexity level and tags

### 3.4 Session Memory Capture
**When to Capture Session Memory:**
- Completing significant multi-step work
- Making important architectural decisions
- Discovering valuable insights
- Solving complex problems

**Session Memory Creation:**
```bash
# Create session memory
cd .devin/memory/sessions
vim YYYY-MM-DD-session-description.md
```

**Include in Session Memory:**
- Work completed
- Decisions made with rationale
- Issues encountered and resolved
- Files modified
- Next steps identified

## Phase 4: Verification

### 4.1 Testing
- Run relevant tests
- Test affected functionality
- Verify documentation accuracy
- Check for broken links

### 4.2 Documentation Validation
```bash
# Validate CHANGELOG format
python3 scripts/changelog-manager.py validate

# Check documentation links (manual or automated)
# Verify all "Last Updated" fields are current
```

### 4.3 System Verification
```bash
# Use trade-verify skill for system health
# Run configuration validation
./scripts/validate-configs.sh

# Test automation scripts if relevant
```

## Phase 5: Integration

### 5.1 Pre-Commit Checklist
- [ ] CHANGELOG updated with all changes
- [ ] Documentation updated for user-facing changes
- [ ] Knowledge base updated if patterns discovered
- [ ] Workflows created if procedures documented
- [ ] Session memory captured for significant work
- [ ] All "Last Updated" fields current
- [ ] CHANGELOG format validated
- [ ] Tests passing
- [ ] Documentation links verified

### 5.2 Commit Process
```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Feature: description of changes

- Change 1
- Change 2
- Change 3

Related documentation: docs/feature/doc.md
Knowledge article: docs/knowledge/category/article.md"

# Or use the conventional commit format
git commit -m "feat: add new trading signal

- Implemented RSI signal calculation
- Added signal to configuration
- Updated documentation

Closes #123"
```

### 5.3 Release Process (for releases)
```bash
# Validate CHANGELOG
python3 scripts/changelog-manager.py validate

# Review [Unreleased] entries
# Ensure completeness and accuracy

# Create release
python3 scripts/changelog-manager.py release 1.2.3

# Tag the release
git tag -a v1.2.3 -m "Release version 1.2.3"

# Push changes and tags
git push origin main
git push origin v1.2.3
```

## Daily Development Practices

### Morning Routine
1. Check CHANGELOG for recent changes
2. Review knowledge base for relevant patterns
3. Check for new workflows or procedures
4. Review session memory from previous work

### During Development
1. Update CHANGELOG as you complete changes
2. Consult knowledge base for patterns
3. Follow existing workflows for procedures
4. Note insights for knowledge capture

### End of Day
1. Review documentation updates made
2. Capture session memory if significant work done
3. Update knowledge base if insights discovered
4. Ensure CHANGELOG is current

## Documentation Maintenance Schedule

### Daily
- Update CHANGELOG with changes made
- Update "Last Updated" fields for modified docs
- Capture session memory for significant work

### Weekly
- Review knowledge base for new content
- Check for documentation gaps
- Verify workflow procedures are current
- Update documentation indices if needed

### Monthly
- Review and update knowledge articles
- Archive outdated content per retention policy
- Check for broken documentation links
- Standardize "Last Updated" fields across all docs

### Quarterly
- Comprehensive documentation review
- Archive evaluation per retention policy
- Documentation standards review and update
- Knowledge base audit for relevance

## Tool Usage Guidelines

### CHANGELOG Tools
**Use `update-changelog.sh` for:**
- Quick, simple entries during development
- Routine change documentation
- When you don't need advanced features

**Use `changelog-manager.py` for:**
- Pre-release validation
- Complex changelog operations
- Version releases
- Format validation

### Knowledge Base
**When to consult:**
- Starting a new feature or task
- Encountering a problem
- Looking for best practices
- Needing implementation patterns

**When to contribute:**
- Discovering reusable approaches
- Learning valuable lessons
- Solving complex problems
- Identifying best practices

### Workflow Procedures
**When to consult:**
- Performing operational tasks
- Following established procedures
- Troubleshooting systematically
- Deploying changes

**When to create:**
- Documenting repeatable processes
- Standardizing procedures
- Capturing troubleshooting methods
- Creating deployment guides

### Memory Capture
**When to capture session memory:**
- Completing significant work
- Making architectural decisions
- Learning valuable insights
- Solving complex problems

**When to capture learnings:**
- Discovering something valuable
- Understanding system behavior
- Identifying effective approaches
- Learning from mistakes

**When to capture patterns:**
- Identifying reusable solutions
- Documenting effective approaches
- Creating design patterns
- Establishing best practices

## Integration with Existing Skills

### trade-verify
- Use for system health verification
- Check documentation completeness
- Validate configuration consistency
- Test after documentation changes

### config-helper
- Use when updating configuration
- Document configuration patterns
- Capture configuration learnings
- Create configuration workflows

### remote-access
- Document remote procedures
- Capture remote operation patterns
- Create troubleshooting workflows
- Note remote access learnings

### browser-helper
- Document UI testing procedures
- Capture UI patterns
- Create browser automation workflows
- Note UI testing insights

## Troubleshooting Documentation Issues

### CHANGELOG Validation Fails
```bash
# Check what's wrong
python3 scripts/changelog-manager.py validate

# Fix missing subsections
# Ensure proper format
# Check version format
```

### Broken Documentation Links
- Use grep to find references to moved/deleted docs
- Update all cross-references
- Check INDEX.md and PORTAL.md
- Update category indices

### Outdated "Last Updated" Fields
```bash
# Standardize all dates
python3 scripts/standardize-last-updated.py

# Or set specific date
python3 scripts/standardize-last-updated.py --date 2026-08-04
```

### Knowledge Base Gaps
- Identify missing topics during development
- Create knowledge articles when discovering patterns
- Encourage team to contribute insights
- Review during quarterly documentation review

## Metrics and Improvement

### Track
- CHANGELOG compliance rate
- Knowledge base growth
- Workflow documentation coverage
- Session memory capture frequency
- Documentation review completion

### Improve
- Adjust workflow based on team feedback
- Refine documentation standards
- Optimize tool usage
- Enhance automation where beneficial

## Related Documentation

- [Documentation Portal](PORTAL.md) - Navigation and discovery
- [Documentation Index](INDEX.md) - Complete documentation listing
- [CHANGELOG](../CHANGELOG.md) - Version history
- [Archive Retention Policy](ARCHIVE_RETENTION_POLICY.md) - Archive management
- [AGENTS.md](../AGENTS.md) - Sub-agent usage patterns

---

**Last Updated:** 2026-08-04
**Workflow Version:** 1.0
**Maintainer:** trade development team
