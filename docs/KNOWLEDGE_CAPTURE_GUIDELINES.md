# Knowledge Capture Guidelines

This document provides guidelines for capturing and managing knowledge across the trade project's knowledge systems: knowledge base, memory capture, and workflow documentation.

## Overview

The project has three knowledge capture systems:
1. **Knowledge Base** (`docs/knowledge/`) - Formalized articles and patterns
2. **Memory System** (`.devin/memory/`) - Session records, learnings, and patterns
3. **Workflow Documentation** (`docs/workflows/`) - Operational procedures

## When to Capture Knowledge

### Knowledge Base (`docs/knowledge/`)

**Capture in Knowledge Base when:**
- ✅ Discovering a reusable pattern or approach
- ✅ Learning something that could help future work
- ✅ Solving a complex problem with a good solution
- ✅ Identifying best practices or anti-patterns
- ✅ Documenting architectural decisions and rationale
- ✅ Capturing performance insights and optimizations
- ✅ Recording troubleshooting solutions for common issues

**Don't capture in Knowledge Base when:**
- ❌ Information is temporary or quickly changing
- ❌ Content is specific to a single session
- ❌ Information is already well-documented elsewhere
- ❌ Content lacks broader applicability

### Memory System (`.devin/memory/`)

**Capture Session Memory when:**
- ✅ Completing significant multi-step work
- ✅ Making important architectural decisions
- ✅ Discovering valuable insights during development
- ✅ Solving complex problems
- ✅ Ending a productive work session

**Capture Learnings when:**
- ✅ Discovering something valuable about the system
- ✅ Understanding system behavior or characteristics
- ✅ Identifying effective approaches or techniques
- ✅ Learning from mistakes or failures
- ✅ Gaining insights that could inform future work

**Capture Patterns when:**
- ✅ Identifying reusable solutions or approaches
- ✅ Documenting effective design patterns
- ✅ Establishing coding or architectural patterns
- ✅ Creating process or workflow patterns
- ✅ Defining best practice patterns

### Workflow Documentation (`docs/workflows/`)

**Create Workflows when:**
- ✅ Documenting a repeatable multi-step process
- ✅ Creating procedures for operational tasks
- ✅ Capturing troubleshooting methodologies
- ✅ Standardizing deployment or maintenance procedures
- ✅ Documenting cross-system operational processes

**Don't create Workflows when:**
- ❌ Process is one-time or unlikely to be repeated
- ❌ Procedure is simple and self-evident
- ❌ Content is better suited for knowledge base
- ❌ Process is already well-documented

## Knowledge Capture Process

### Knowledge Base Articles

**1. Identify the Need**
- During development: "This pattern could be useful again"
- During problem-solving: "This solution should be documented"
- During review: "We're solving this problem repeatedly"

**2. Choose the Right Category**
- **Architecture**: Design decisions, system insights, integration patterns
- **Operations**: Deployment, monitoring, maintenance procedures
- **Troubleshooting**: Diagnostic approaches, common solutions
- **Best Practices**: Development standards, coding patterns, security practices

**3. Create the Article**
```bash
# Navigate to appropriate category
cd docs/knowledge/[category]

# Create article using template
vim your-article-name.md
```

**4. Follow the Template**
```markdown
# Article Title

## Problem
What problem does this address?

## Context
Background information and prerequisites

## Solution
The recommended approach or solution

## Implementation
How to implement (if applicable)

## Rationale
Why this solution is recommended

## Alternatives Considered
Other approaches and why they weren't chosen

## Related Knowledge
Links to related articles and documentation

## References
External references or sources

## Last Updated
Date and contributor

---
**Tags:** tag1, tag2, tag3
**Category:** category
**Complexity:** low/medium/high
```

**5. Update the Index**
- Add your article to the category's README.md
- Include a brief description
- Add relevant tags for discoverability

### Memory System Entries

**Session Memory**
```bash
cd .devin/memory/sessions
vim YYYY-MM-DD-session-description.md
```

**Include:**
- Work completed
- Decisions made with rationale
- Issues encountered and resolved
- Files modified
- Next steps identified
- Related sessions or documentation

**Learnings**
```bash
cd .devin/memory/learnings
vim topic-description.md
```

**Include:**
- Context of the discovery
- What was learned
- Why it matters
- How to apply it in future
- Related documentation or code

**Patterns**
```bash
cd .devin/memory/patterns
vim pattern-name.md
```

**Include:**
- When the pattern is applicable
- What problem it solves
- The solution approach
- Implementation details
- Benefits and trade-offs
- Examples and alternatives

### Workflow Documentation

**1. Identify the Procedure**
- Operational task that needs documentation
- Multi-step process that should be standardized
- Troubleshooting approach that should be captured

**2. Create the Workflow**
```bash
cd docs/workflows
vim workflow-name.md
```

**3. Follow the Template**
```markdown
# Workflow Name

## Purpose
Brief description of what this workflow accomplishes

## Prerequisites
Required tools, access, or conditions

## Steps
1. Step one with details
2. Step two with details
3. Step three with details

## Verification
How to verify successful completion

## Troubleshooting
Common issues and solutions

## Related Workflows
Links to related procedures

## Last Updated
Date and maintainer

---
**Tags:** tags
**Category:** category
**Complexity:** low/medium/high
```

**4. Update the Index**
- Add to appropriate category in workflows/README.md
- Include complexity level and tags

## Quality Guidelines

### Knowledge Base Articles

**Characteristics of Good Articles:**
- **Specific**: Addresses a clear problem or topic
- **Actionable**: Provides concrete guidance
- **Contextual**: Includes background and rationale
- **Referenced**: Links to related documentation
- **Current**: Maintained and updated as needed
- **Tagged**: Uses relevant tags for discoverability

**Writing Guidelines:**
- Focus on "why" and "how" rather than just "what"
- Include examples where helpful
- Consider edge cases and alternatives
- Explain trade-offs and considerations
- Keep implementation details current

### Memory System Entries

**Session Memory:**
- Be comprehensive but concise
- Focus on decisions and their rationale
- Note obstacles and how they were overcome
- Identify clear next steps
- Cross-reference related work

**Learnings:**
- Capture the insight clearly and specifically
- Explain the context thoroughly
- Describe why it matters
- Provide application guidance
- Add relevant tags

**Patterns:**
- Document the pattern clearly
- Specify when to use it
- Provide implementation guidance
- Explain benefits and trade-offs
- Include concrete examples

### Workflow Documentation

**Characteristics of Good Workflows:**
- **Step-by-step**: Clear, sequential procedures
- **Complete**: Covers the entire process
- **Verifiable**: Includes success criteria
- **Troubleshooted**: Addresses common issues
- **Maintained**: Updated as processes change

**Writing Guidelines:**
- Number steps clearly
- Include commands with expected outputs
- Provide verification steps
- Address common pitfalls
- Include rollback procedures if applicable

## Integration with Development Workflow

### During Development

**Planning Phase:**
- Consult knowledge base for relevant patterns
- Review related workflows for procedures
- Check memory system for relevant learnings

**Development Phase:**
- Note insights for knowledge capture
- Document patterns as they're discovered
- Record learnings as they occur

**Completion Phase:**
- Capture session memory for significant work
- Create knowledge articles for reusable insights
- Document workflows for repeatable processes

### During Code Review

**Reviewers Should Check:**
- Are relevant knowledge articles referenced?
- Should new knowledge be captured?
- Are workflows documented for new procedures?
- Is session memory appropriate for the work?

### During Documentation Review

**Quarterly Review:**
- Review knowledge base for relevance
- Update outdated articles
- Archive obsolete content
- Identify gaps in documentation

## Knowledge Maintenance

### Knowledge Base

**Monthly:**
- Review new articles for quality
- Update indices as needed
- Check for broken links
- Ensure tags are relevant

**Quarterly:**
- Comprehensive review of all articles
- Archive outdated content
- Update based on system changes
- Identify gaps in coverage

**Annually:**
- Evaluate knowledge base effectiveness
- Review category organization
- Update templates if needed
- Assess capture guidelines

### Memory System

**Monthly:**
- Review recent session memory
- Extract reusable insights for knowledge base
- Archive old session memory
- Update patterns and learnings

**Quarterly:**
- Comprehensive memory review
- Migrate valuable content to knowledge base
- Archive obsolete memory entries
- Update capture guidelines

### Workflow Documentation

**Monthly:**
- Review workflow accuracy
- Update procedures as they change
- Add new workflows as needed
- Archive outdated workflows

**Quarterly:**
- Comprehensive workflow review
- Test procedures for accuracy
- Update based on system changes
- Archive per retention policy

## Discoverability

### Tagging Strategy

**Knowledge Base Tags:**
- Use specific, descriptive tags
- Include system area (api, database, ui, etc.)
- Include topic (performance, security, etc.)
- Include complexity (simple, complex)

**Memory System Tags:**
- Use context-specific tags
- Include discovery context
- Include applicability (when to use)
- Cross-reference with documentation

**Workflow Tags:**
- Include operational area
- Include complexity level
- Include frequency of use
- Include related systems

### Search Strategy

**When Looking for Knowledge:**
1. Search by tags for specific topics
2. Browse by category for broader context
3. Use the main index for overview
4. Cross-reference with documentation
5. Check memory system for recent insights

## Team Guidelines

### For Individual Developers

**Daily:**
- Note insights during development
- Update session memory for significant work
- Consult knowledge base before starting tasks

**Weekly:**
- Review new knowledge articles
- Update personal learnings
- Contribute patterns as discovered

**Monthly:**
- Review knowledge base for gaps
- Update personal contributions
- Suggest improvements to guidelines

### For Teams

**Sprint Planning:**
- Consult knowledge base for relevant patterns
- Review workflows for procedures
- Check memory system for relevant learnings

**Sprint Review:**
- Capture knowledge from completed work
- Update workflows for new procedures
- Document patterns and insights

**Retrospectives:**
- Identify knowledge gaps
- Discuss capture process improvements
- Plan knowledge capture for next sprint

## Metrics and Improvement

### Track
- Knowledge base article creation rate
- Memory system entry frequency
- Workflow documentation coverage
- Knowledge search success rate
- Team satisfaction with knowledge systems

### Improve
- Adjust capture guidelines based on usage
- Refine categorization and tagging
- Improve discoverability
- Enhance templates and processes
- Streamline capture procedures

## Examples

### Knowledge Base Article Example
*Developer discovers a better way to handle database connections:*
1. Recognizes this as a reusable pattern
2. Creates article in `docs/knowledge/architecture/db-connection-pattern.md`
3. Includes problem, solution, rationale, and code examples
4. Updates architecture knowledge index
5. Tags with "database", "patterns", "performance"

### Session Memory Example
*Developer completes a complex feature implementation:*
1. Creates session memory in `.devin/memory/sessions/2026-08-04-feature-implementation.md`
2. Documents decisions made and issues encountered
3. Notes files modified and next steps
4. Cross-references related documentation

### Workflow Example
*Team standardizes deployment process:*
1. Documents procedure in `docs/workflows/deployment.md`
2. Includes step-by-step instructions
3. Adds verification and troubleshooting sections
4. Updates workflow index
5. Tags with "deployment", "operations", "medium-complexity"

## Related Documentation

- [Knowledge Base](knowledge/README.md) - Knowledge base structure
- [Memory System](../.devin/memory/README.md) - Memory system documentation
- [Workflow Archive](workflows/README.md) - Workflow documentation
- [Development Workflow](DEVELOPMENT_WORKFLOW.md) - Overall development process
- [Archive Retention Policy](ARCHIVE_RETENTION_POLICY.md) - Archive management

---

**Last Updated:** 2026-08-04
**Guidelines Version:** 1.0
**Maintainer:** trade development team
