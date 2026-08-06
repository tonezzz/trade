
---

**Last Updated:** 2026-08-06
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
- **External Data Integration**: Alpha Vantage MCP for financial data, commodity price validation

### Existing Skills That Can Delegate:
- **trade-verify**: Can delegate parallel health checks to sub-agents
- **remote-access**: Can delegate remote troubleshooting to sub-agents
- **config-helper**: Can delegate complex configuration updates to sub-agents
- **browser-helper**: Can delegate UI testing to sub-agents
- **deployment-sync**: Can delegate deployment investigation and file synchronization to sub-agents

## MCP Server Integration

### Alpha Vantage MCP Server
The project uses the Alpha Vantage MCP server for financial data access and validation:

**Configuration**: Located in `~/.config/devin/mcp_config.json`
```json
"alphavantage": {
  "url": "https://mcp.alphavantage.co/mcp?apikey=KUTH6I3J1OORWZI8",
  "disabled": false
}
```

**Available Tools**: 100+ Alpha Vantage functions including:
- Stock market data (TIME_SERIES_DAILY, TIME_SERIES_INTRADAY, etc.)
- Commodity prices (WTI, BRENT, WHEAT, CORN, COPPER, etc.)
- Forex rates (FX_DAILY, CURRENCY_EXCHANGE_RATE)
- Technical indicators (SMA, EMA, RSI, MACD, etc.)
- Economic indicators (GDP, CPI, UNEMPLOYMENT, etc.)

**Usage in Data Quality Agent**:
- `scripts/data_quality_agent.py` uses Alpha Vantage API for commodity price validation
- Maps internal symbols to Alpha Vantage function names (e.g., WHEAT→WHEAT, WTI→WTI)
- Falls back to MetalPrices API for precious metals (XAU, XAG) not directly available via Alpha Vantage commodities
- Provides real-time price validation against database values

**Key Functions Used**:
- `WTI` - Crude Oil WTI prices
- `BRENT` - Brent Crude prices  
- `WHEAT` - Global Wheat prices
- `CORN` - Corn prices
- `COPPER` - Copper prices
- `NATURAL_GAS` - Natural Gas prices

**Benefits**:
- Unified API access to 100+ financial data endpoints
- Automatic function discovery via MCP
- Consistent error handling and rate limiting
- No hardcoded API function names
- Future-proof access to new Alpha Vantage features

**Limitations**:
- Precious metals (GOLD/XAU, SILVER/XAG) not available via commodity functions
- Requires fallback to MetalPrices API for precious metals validation
- Free tier has rate limits (25 requests/day for direct API, higher via MCP)

**Integration Status**: ✅ Completed (2026-08-06)
- MCP server successfully configured and tested
- Data quality agent updated to use correct Alpha Vantage API functions
- Commodity price validation working for WHEAT, CORN, BRENT
- Precious metals using MetalPrices API fallback
- Validation success rate: 29.4% (existing data quality issues, not MCP-related)

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
