# Memory Capture System

This directory contains the memory capture system for the Dollar Price Database project. Memories are insights, decisions, and learnings captured during development sessions.

## Purpose

The memory system serves as:
- **Decision Log**: Capture technical decisions and their rationale
- **Knowledge Base**: Store insights and patterns discovered during development
- **Troubleshooting Record**: Document solutions to problems encountered
- **Process Improvements**: Record workflow optimizations and lessons learned

## Structure

```
.devlin/memory/
├── README.md                    # This file
├── decisions/                   # Technical decisions and rationale
│   ├── infrastructure.md
│   ├── api-design.md
│   └── data-model.md
├── insights/                    # Insights and discoveries
│   ├── performance.md
│   ├── integration.md
│   └── user-behavior.md
├── troubleshooting/             # Problem solutions
│   ├── deployment.md
│   ├── api-issues.md
│   └── configuration.md
└── workflows/                  # Process improvements
    ├── development.md
    ├── deployment.md
    └── documentation.md
```

## Memory Entry Template

When creating a new memory entry, use this template:

```markdown
# [Title]

**Category:** [decisions/insights/troubleshooting/workflows]  
**Date:** YYYY-MM-DD  
**Session:** [Session context if applicable]  
**Tags:** [tag1, tag2, tag3]

## Context
[Describe the situation or problem that led to this memory]

## Decision/Insight/Solution
[Describe the decision, insight, or solution]

## Rationale/Why It Works
[Explain the reasoning behind the decision or why the solution works]

## Impact
[Describe the impact of this decision or solution]

## Related Memories
- [Link to related memory entries]
- [Link to standard documentation]
```

## When to Create Memories

Create memory entries when:
- Making significant technical decisions
- Discovering non-obvious insights about the system
- Solving complex problems that could recur
- Optimizing workflows or processes
- Learning lessons that could help others

## Memory vs. Documentation

| Memory System | Standard Documentation |
|---------------|----------------------|
| Decisions and rationale | How-to guides and references |
| Insights and discoveries | Feature documentation |
| Problem solutions | Troubleshooting guides |
| Process improvements | Workflow documentation |
| Informal, evolving | Structured, versioned |
| Quick capture | Comprehensive coverage |

## Maintenance

- Review memories quarterly for relevance
- Archive outdated memories to `docs-archive/`
- Cross-reference with standard documentation
- Update when decisions change or new insights emerge

## Search Strategy

When looking for information:
1. Check standard documentation first (docs/)
2. Search memory system for decisions and insights
3. Check knowledge base (docs/knowledge/) for patterns
4. Consult archived docs for historical context

## Related Systems

- [Knowledge Base](../../docs/knowledge/README.md) - Patterns and best practices
- [Decision Log](../../docs/core/DECISION_LOG.md) - Formal technical decisions
- [CHANGELOG](../../CHANGELOG.md) - Version history and changes

---

**Last Updated:** 2026-08-04  
**Maintainer:** trade development team