
---

**Last Updated:** 2026-08-04
# Sub-Agent Guidelines for Trade Project

## Overview
This document defines when and how to use sub-agents for the Dollar Price Database project. Sub-agents help with parallel execution, complex exploration, and keeping context clean.

## When to Use Sub-Agents

### Use `subagent_explore` (Read-Only)
Use for codebase exploration, research, and search tasks that don't require modifications:

- **Architecture Investigation**: Tracing dependencies between API, database, UIs, automation
- **Documentation Research**: Cross-referencing multiple docs files, finding patterns
- **Code Pattern Analysis**: Finding how similar features are implemented
- **Impact Analysis**: Understanding what files a change might affect
- **Configuration Research**: Understanding SSOT structure and relationships
- **Performance Investigation**: Finding bottlenecks or optimization opportunities

### Use `subagent_general` (Full Access)
Use for multi-step tasks that require write access or command execution:

- **Parallel Infrastructure Tasks**: Health checks across multiple machines simultaneously
- **Multi-Service Verification**: Testing API, database, and UIs together
- **Complex Deployments**: Multi-stage deployment with verification
- **End-to-End Testing**: Complete workflow testing across services
- **Configuration Updates**: Synchronized changes across multiple config files
- **Documentation Updates**: Multi-file documentation improvements

## Project-Specific Patterns

### Multi-Machine Operations
```python
# Parallel health checks
subagent_general("Check tony-omen services")
subagent_general("Check tony-dell services")

# Synchronized configuration updates
subagent_general("Update screen timeout configuration on both tony-omen and tony-dell")
```

### SSOT Configuration Tasks
```python
# Validate and sync configurations
subagent_explore("Research SSOT structure and relationships")
# Then make changes
subagent_general("Update infrastructure.yml and sync to remote")
```

### Documentation Work
```python
# Research phase
subagent_explore("Find all references to WebSocket in docs")
# Implementation phase
subagent_general("Update WebSocket documentation across all files")
```

### Feature Implementation
```python
# Research existing patterns
subagent_explore("Find how other trading signals are implemented")
# Implement new feature
subagent_general("Implement new RSI signal following existing patterns")
```

## Anti-Patterns to Avoid

### DON'T use sub-agents for:
- **Single file edits**: Use edit tool directly
- **Simple grep/search**: Use grep tool directly
- **Known file paths**: Read files directly instead of delegating
- **Single commands**: Execute commands directly
- **Quick questions**: Answer directly if you know the answer

### DO use sub-agents for:
- **Uncertain exploration**: When you need to search broadly
- **Parallel work**: When tasks can run simultaneously
- **Complex multi-step**: When work has many interdependent steps
- **Context isolation**: When work is unrelated to current task
- **Background work**: When you want to continue while it runs

## Communication Patterns

### When delegating to sub-agents:
1. **Front-load context**: Provide all relevant file paths, function names, existing patterns
2. **Be specific**: Clearly state what you need back (investigation vs implementation)
3. **Set expectations**: Specify if changes should be made or if it's read-only
4. **Define scope**: Limit to specific areas to avoid scope creep

### Example good prompts:
```
"Investigate how the backtesting system handles signal generation.
Look at src/models.py, config/backtesting.yml, and docs/features/backtesting/.
I need to understand the signal-to-backtest integration flow.
This is read-only research - do not make any changes."
```

```
"Implement a new MACD signal following the existing RSI signal pattern.
Use src/models.py, config/signals.yml as templates.
Update docs/features/signals/SIGNALS.md with the new signal.
Make the changes directly - this is implementation work."
```

## Project-Specific Context

### Key Areas for Sub-Agent Use:
- **SSOT Management**: config/ directory, infrastructure.yml, deployment scripts
- **Documentation System**: docs/, docs-archive/, cross-referencing
- **Multi-Service Testing**: API, database, WebSocket, UIs
- **Remote Operations**: tony-dell via MCP server, service management
- **Feature Development**: Signals, backtesting, automation, UI integration
- **System Configuration**: Screen timeout, power management, notification systems

### Existing Skills That Can Delegate:
- **trade-verify**: Can delegate parallel health checks to sub-agents
- **remote-access**: Can delegate remote troubleshooting to sub-agents
- **config-helper**: Can delegate complex configuration updates to sub-agents
- **browser-helper**: Can delegate UI testing to sub-agents

## Verification

After sub-agent completion:
1. Review changes for consistency with project patterns
2. Run relevant verification (trade-verify skill, tests, health checks)
3. Update documentation if needed
4. Commit changes with clear messages

## Iteration

This is a living document. Update it based on:
- What sub-agent patterns work well for this project
- New infrastructure or service additions
- Changes in team workflow or preferences
- Lessons learned from sub-agent successes/failures
