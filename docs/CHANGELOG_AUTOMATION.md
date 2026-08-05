# CHANGELOG Automation

This document describes the CHANGELOG automation system for the Dollar Price Database project.

## Overview

The CHANGELOG automation system provides a command-line helper script to simplify updating the CHANGELOG.md file following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

## Script Location

`scripts/update-changelog.sh`

## Usage

### Basic Usage

```bash
./scripts/update-changelog.sh <category> "<message>"
```

### Categories

- `added` - New features
- `changed` - Changes in existing functionality  
- `deprecated` - Soon-to-be removed features
- `removed` - Removed features
- `fixed` - Bug fixes
- `security` - Security vulnerabilities or improvements

### Examples

```bash
# Add a new feature
./scripts/update-changelog.sh added "New trading signal for RSI"

# Fix a bug
./scripts/update-changelog.sh fixed "Fixed WebSocket connection timeout"

# Document a change
./scripts/update-changelog.sh changed "Updated API response format for exchange rates"
```

## How It Works

1. The script validates the category and message
2. It reads the existing CHANGELOG.md file
3. It inserts the new entry under the correct category in the `[Unreleased]` section
4. It creates a temporary file and replaces the original
5. It provides feedback on the changes made

## Output Format

The script adds entries in this format:

```markdown
## [Unreleased]

### Added
- New trading signal for RSI
- Knowledge base structure (docs/knowledge/) with patterns and best practices

### Fixed
- Fixed WebSocket connection timeout
```

## After Running the Script

After the script updates the CHANGELOG, you should:

1. **Review the changes**:
   ```bash
   git diff CHANGELOG.md
   ```

2. **Commit the changes**:
   ```bash
   git add CHANGELOG.md
   git commit -m "docs: update changelog"
   ```

## Integration with Workflow

### When to Update CHANGELOG

Update the CHANGELOG when:
- Adding new features
- Making breaking changes
- Fixing bugs
- Deprecating functionality
- Making security improvements

### Before Release

Before creating a release:
1. Review all entries in `[Unreleased]`
2. Create a new version section (e.g., `[1.1.0] - 2026-08-05`)
3. Move entries from `[Unreleased]` to the new version section
4. Update the version number following semantic versioning

## Versioning Convention

- **Major (X.0.0)**: Breaking changes, major architectural changes
- **Minor (0.X.0)**: New features, significant enhancements  
- **Patch (0.0.X)**: Bug fixes, minor improvements, documentation updates

## Troubleshooting

### Script Not Executable

```bash
chmod +x scripts/update-changelog.sh
```

### Invalid Category

The script will show an error if you use an invalid category. Use one of: `added`, `changed`, `deprecated`, `removed`, `fixed`, `security`.

### CHANGELOG.md Not Found

Ensure you're running the script from the project root directory where CHANGELOG.md exists.

## Manual Updates

You can also manually edit CHANGELOG.md following the Keep a Changelog format. The script is a convenience tool, not a requirement.

## Related Documentation

- [CHANGELOG.md](../CHANGELOG.md) - The actual changelog file
- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) - Format specification
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html) - Versioning specification

---

**Last Updated:** 2026-08-04  
**Maintainer:** trade documentation team