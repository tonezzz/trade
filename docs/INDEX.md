
---

**Last Updated:** 2026-08-05
# Trade Documentation Index

Complete documentation for the Dollar Price Database system: historical USD exchange rates, Dollar Index (DXY), commodity prices, trading signals, and backtesting.

**🌐 [Documentation Portal](PORTAL.md)** - Unified documentation hub with guided navigation

---

## 🚀 Quick Start

**New to the trade system?** Start here:
- [Documentation Portal](PORTAL.md) - Guided documentation experience
- [Main README](../README.md) - Project overview and quick start guide
- [Getting Started](#getting-started) - Setup and installation
- [System Overview](#system-overview) - Architecture and components

---

## 📋 Project Information

- [CHANGELOG](../CHANGELOG.md) - Version history and notable changes
- [CHANGELOG Automation](CHANGELOG_AUTOMATION.md) - Guide for updating the changelog
- [Project Status](../README.md#current-status) - Current implementation status
- [Configuration Management](../CONFIGURATION_MANAGEMENT.md) - SSOT and configuration guide
- [Contributing Guide](../CONTRIBUTING.md) - Contribution guidelines and process
- [Agent Guidelines](../AGENTS.md) - Sub-agent usage guidelines

## 📖 Documentation Management

- [Development Workflow](DEVELOPMENT_WORKFLOW.md) - Integrated development workflow with documentation systems
- [CHANGELOG Workflow](CHANGELOG_WORKFLOW.md) - CHANGELOG automation procedures and best practices
- [Knowledge Capture Guidelines](KNOWLEDGE_CAPTURE_GUIDELINES.md) - Guidelines for capturing knowledge across systems
- [Documentation Review Schedule](DOCUMENTATION_REVIEW_SCHEDULE.md) - Schedule and procedures for documentation maintenance
- [Archive Management Procedures](ARCHIVE_MANAGEMENT_PROCEDURES.md) - Operational procedures for archive management
- [Doc Coordinator Report](DOC_COORDINATOR_REPORT.md) - Documentation quality assessment and improvements

---

## 📚 Getting Started

### Quick Start
- [Quick Start Guide](getting-started/quickstart.md) - Get the trade system up and running in minutes

### Prerequisites
- Python 3.14+
- PostgreSQL database
- Docker (for containerized deployment)

### Setup Guides
- [Installation](../README.md#quick-start) - Install dependencies and setup database
- [First Steps](../README.md#quick-start) - Download sample data and import
- [Database Setup](core/DEPLOYMENT.md) - Database configuration and optimization
- [CLI Usage](../README.md#quick-start) - Command-line interface basics

---

## 🏗️ System Overview

### Architecture
- [Architecture](core/ARCHITECTURE.md) - System architecture and technical design
- [Project Plan](reference/PROJECT_PLAN.md) - Project vision, phases, and timeline
- [Decision Log](core/DECISION_LOG.md) - Technical decisions and rationale

### Components
- **FastAPI Backend** - REST API for data access
- **PostgreSQL Database** - Relational data storage with optimized indexes
- **CLI Tool** - Command-line interface for data management
- **Visualization System** - Interactive Plotly charts
- **Automation System** - Scheduled data downloads and imports

---

## 🔧 Core Documentation

### API Reference
- [API Guide](core/API_GUIDE.md) - Complete API reference and examples
  - Endpoints - All available API routes
  - Authentication - Security and access control
  - Examples - Usage examples and code samples
  - WebSocket - Real-time data streaming

### Deployment
- [Deployment Guide](core/DEPLOYMENT.md) - Deployment and configuration
  - Docker setup - Containerized deployment
  - Environment variables - Configuration options
  - Database setup - PostgreSQL configuration
  - Health checks - System monitoring

### Troubleshooting
- [Troubleshooting](core/TROUBLESHOOTING.md) - Common issues and solutions
  - Database issues - Connection and query problems
  - API issues - Endpoint errors and debugging
  - Data import issues - CSV import problems
  - Performance issues - Optimization tips

---

## 🧠 Knowledge Base

Insights, patterns, lessons learned, and best practices accumulated during development.

- [Knowledge Base Overview](knowledge/README.md) - Knowledge base guide and structure
- [Lessons Learned](knowledge/lessons/lessons-learned.md) - Comprehensive lessons from development
- [Best Practices](knowledge/best-practices/best-practices.md) - Project-specific best practices
- [Patterns](knowledge/patterns/patterns.md) - Architectural and design patterns
- [API Patterns](knowledge/patterns/api-patterns.md) - Reusable API patterns
- [SSOT Configuration Pattern](knowledge/architecture/ssot-configuration-pattern.md) - Single Source of Truth configuration pattern
- [Code Conventions](knowledge/best-practices/code-conventions.md) - Project-specific code conventions

---

## 📊 Features Documentation

### Trading Signals
- [Signals Overview](features/signals/SIGNALS.md) - Trading signals system
- [Signals Quickstart](features/signals/SIGNALS_QUICKSTART.md) - Quick start for signals
- [Signals Implementation](features/signals/SIGNALS_IMPLEMENTATION_SUMMARY.md) - Implementation details

### Backtesting
- [Backtesting Guide](features/backtesting/BACKTESTING.md) - Backtesting system guide
- [Backtesting Summary](features/backtesting/BACKTESTING_SUMMARY.md) - Backtesting implementation summary

### WebSocket
- [WebSocket Guide](features/websocket/WEBSOCKET.md) - WebSocket implementation
- [WebSocket Summary](features/websocket/WEBSOCKET_IMPLEMENTATION_SUMMARY.md) - Implementation details

### User Interfaces
- [TradeCanvas Integration](features/ui/TRADECANVAS_INTEGRATION.md) - TradeCanvas UI setup
- [TradeCanvas Quickstart](features/ui/TRADECANVAS_QUICKSTART.md) - Quick start for TradeCanvas
- [Wick Integration](features/ui/WICK_INTEGRATION.md) - Wick UI integration
- [UI Comparison](features/ui/UI_COMPARISON_EVALUATION.md) - UI feature comparison
- [Trading Terminal](features/ui/TRADING_TERMINAL_INTEGRATION.md) - Trading terminal setup
- [Trading Terminal Quickstart](features/ui/TRADING_TERMINAL_QUICKSTART.md) - Quick start for terminal

### Automation
- [Automation Quickstart](features/automation/AUTOMATION_QUICK_START.md) - Quick start for automation

### Visualization
- [Visualization Guide](core/VISUALIZATION_GUIDE.md) - Interactive charting system
  - Plotly charts - Chart types and customization
  - Data visualization - Best practices
  - Examples - Sample visualizations

---

## 📈 Data Documentation

### Data Sources
- [Data Sources](data/DATA_SOURCES.md) - Historical data source documentation
  - Exchange rates - Currency data sources
  - Dollar Index - DXY data sources
  - Commodity prices - Oil, gold, and other commodities
  - API endpoints - Data provider APIs

### Data Management
- [Data Import](../README.md#quick-start) - CSV import process
- [Data Validation](../README.md#quick-start) - Data quality checks
- [Data Download](../download_data.py) - Automated data download scripts

---

## 🛠️ Skills

Located in [`.devin/skills/`](../.devin/skills/)

- [Browser Helper](../.devin/skills/browser-helper/SKILL.md) - Browser automation helper
- [Config Helper](../.devin/skills/config-helper/SKILL.md) - Configuration management
- [Remote Access](../.devin/skills/remote-access/SKILL.md) - Remote access management
- [Trade Verify](../.devin/skills/trade-verify/SKILL.md) - Comprehensive system verification

---

## �️ Workflow Archive System

System for archiving workflows and managing documentation lifecycle.

### Workflow Archive
- [Windsurf Workflows Archive](../.windsurf/workflows/README.md) - Development workflow archives
- [Archive Template](../.windsurf/workflows/archive.md) - Template for workflow archive entries
- [Archival Process](../.windsurf/workflows/ARCHIVAL_PROCESS.md) - Process for archiving workflows
- [Retention Policy](../.windsurf/workflows/RETENTION_POLICY.md) - Retention guidelines and policies
- [Archive Checklist](../.windsurf/workflows/ARCHIVE_CHECKLIST.md) - Checklist for archival process

### Active Workflows
- [Workflows Archive](workflows/README.md) - Active workflow documentation and procedures

### Archive Automation
- [Archive Script](../scripts/archive-docs.sh) - Automated documentation archival script
- [Archive Script Documentation](../scripts/ARCHIVE_DOCS_README.md) - Usage and configuration for archive script

---

## �🔗 Related Projects

### Chaba Infrastructure
- [Chaba Project](../../chaba/README.md) - Main homelab infrastructure
  - Health Check Dashboard - System monitoring
  - Web Services - Caddy and status APIs
  - GPU Services - AI and inference services
  - Documentation - Complete chaba documentation
- [Chaba Documentation Index](../../chaba/docs/INDEX.md) - Complete chaba documentation navigation

---

## 🗄️ Archived Documentation

Historical documentation and strategy documents that have been archived for reference but are no longer actively maintained.

**Location:** [`docs-archive/`](../docs-archive/)

### Available Archives

- **[DEV_FEEDBACK_LOOP_ANALYSIS](../docs-archive/DEV_FEEDBACK_LOOP_ANALYSIS.md)** - Analysis of development feedback loops and optimization strategies
- **[DOCUMENTATION_STRATEGY](../docs-archive/DOCUMENTATION_STRATEGY.md)** - Original documentation strategy and planning
- **[FEEDBACK_LOOP_IMPLEMENTATION](../docs-archive/FEEDBACK_LOOP_IMPLEMENTATION.md)** - Implementation details for feedback loop systems
- **[HANDS_OFF_DEV_STRATEGY](../docs-archive/HANDS_OFF_DEV_STRATEGY.md)** - Strategy for hands-off development approaches
- **[PROJECT_COMPLETION_SUMMARY](../docs-archive/PROJECT_COMPLETION_SUMMARY.md)** - Summary of project completion and achievements

### Why These Are Archived

These documents contain valuable historical context, strategic thinking, and implementation details from earlier phases of the project. They are preserved for:
- Reference when revisiting strategic decisions
- Understanding the evolution of the project
- Learning from past approaches and experiments
- Historical context for new team members

### Archive Maintenance

Archived documents are not actively updated but may contain insights relevant to current work. When referencing archived content:
- Check the date to understand temporal context
- Verify if approaches are still applicable
- Cross-reference with current documentation
- Consider whether content should be moved back to active docs

### Archive Retention Policy

For guidelines on archiving, retention, and disposal of documentation, see:
- [Archive Retention Policy](ARCHIVE_RETENTION_POLICY.md) - Comprehensive archive management guidelines
- [Archive Index](../docs-archive/ARCHIVE_INDEX.md) - Current archive contents and statistics

---

## 📝 Documentation Standards

### Format
- All documentation uses Markdown
- Code blocks with language specification
- Tables for structured data
- Mermaid diagrams for architecture (when applicable)

### Maintenance
- Quarterly documentation review
- Update after major feature changes
- Keep "Last Updated" field current
- Review for broken links quarterly

### Contributing
- Follow existing format patterns
- Add cross-references to related docs
- Update this index when adding new docs
- Include troubleshooting sections where applicable

---

## 📞 Support

For issues or questions:
- Check troubleshooting sections in relevant docs
- Review API guide for endpoint issues
- Use trade-verify skill for system health checks
- Consult chaba infrastructure docs for deployment issues