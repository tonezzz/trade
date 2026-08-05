## [Unreleased]

### Added
- Sub-agent usage guidelines (AGENTS.md and global_rules.md)
- Initial knowledge base article: SSOT Configuration Pattern
- Initial workflow: Configuration Update Workflow
- Initial memory entries: changelog automation approach, layered documentation structure
- Session memory for documentation system improvements
- Development workflow document integrating documentation systems
- CHANGELOG workflow with automation procedures and best practices
- Knowledge capture guidelines for all knowledge systems
- Documentation review schedule with procedures and templates
- Archive management procedures for operational archive handling
- CHANGELOG.md with initial structure and project history
- CHANGELOG automation scripts (update-changelog.sh and changelog-manager.py)
- Knowledge base system (docs/knowledge/) with four categories: architecture, operations, troubleshooting, best-practices
- Workflow archive system (docs/workflows/) with templates and structure
- Unified documentation portal (docs/PORTAL.md) with guided navigation
- Memory capture system (.devin/memory/) for sessions, learnings, and patterns
- Archive retention policy (docs/ARCHIVE_RETENTION_POLICY.md)
- Archive index (docs-archive/ARCHIVE_INDEX.md)
- Script to standardize "Last Updated" fields across documentation (standardize-last-updated.py)

### Changed
- Updated README.md project structure to include new documentation directories
- Integrated archive section into docs/INDEX.md with retention policy links
- Standardized "Last Updated" fields across 37 documentation files to 2026-08-04
- Updated scripts/README.md to include CHANGELOG management documentation
- Enhanced documentation navigation with portal and improved cross-referencing

### Deprecated

### Removed

### Fixed

### Security


## [1.0.0] - 2026-08-04

### Added
- Initial historical price database system
- Multi-type data support (exchange rates, Dollar Index, commodity prices)
- PostgreSQL database with optimized indexes
- Manual CSV import functionality
- Query and analysis functions
- Interactive visualization system with Plotly
- Automated data download and import scheduling
- CLI tool for data management
- FastAPI backend with REST API
- WebSocket implementation for real-time data
- Trading signals system
- Backtesting system
- Multiple UI integrations (TradeCanvas, Wick, Trading Terminal)
- Comprehensive documentation system
- SSOT configuration management
- MCP server for remote execution (tony-dell)
- Configuration automation scripts

### Documentation
- Core documentation (Architecture, API Guide, Deployment, Troubleshooting)
- Feature documentation (Signals, Backtesting, WebSocket, UIs, Automation)
- Data documentation (Data Sources)
- Reference documentation (Project Plan)
- Skills documentation (trade-verify, remote-access, config-helper, browser-helper)
- Configuration management guide


## [0.9.0] - 2026-07-XX

### Added
- Database schema and models
- Basic import functionality
- Initial visualization system
- Data download scripts

### Documentation
- Initial project documentation
- Setup and installation guides

---

## Versioning Convention

- **Major (X.0.0)**: Breaking changes, major architectural changes
- **Minor (0.X.0)**: New features, significant enhancements
- **Patch (0.0.X)**: Bug fixes, minor improvements, documentation updates

## Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerabilities or improvements

---

**Last Updated:** 2026-08-04
