# Contributing to Trade

Thank you for your interest in contributing to the Dollar Price Database project! This document provides guidelines and instructions for contributing code, documentation, and configuration.

---

## Table of Contents

- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Documentation Standards](#documentation-standards)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.14+ installed
- PostgreSQL database access
- Git configured with your credentials
- Basic familiarity with the project structure

### Initial Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub
   git clone https://github.com/your-username/trade.git
   cd trade
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy environment template
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set Up Database**
   ```bash
   # Follow the database setup instructions in README.md
   # Ensure you have a local PostgreSQL instance for development
   ```

4. **Run Initial Tests**
   ```bash
   pytest tests/
   ```

---

## How to Contribute

### Types of Contributions

We welcome contributions in the following areas:

#### Code Contributions
- New features and functionality
- Bug fixes and performance improvements
- Refactoring and code optimization
- Test coverage improvements

#### Documentation Contributions
- Documentation improvements and corrections
- New guides and tutorials
- API documentation updates
- Code comments and docstrings

#### Configuration Contributions
- Configuration file updates
- Deployment script improvements
- Docker and containerization enhancements
- CI/CD pipeline improvements

### Finding Good First Issues

Look for issues labeled:
- `good first issue` - Suitable for new contributors
- `help wanted` - Issues that need community help
- `documentation` - Documentation improvements

### Communication

Before starting major work:
1. Check existing issues and pull requests
2. Open an issue to discuss your approach
3. Get feedback from maintainers
4. Reference the issue in your pull request

---

## Development Workflow

### Branch Strategy

We use a simplified branch workflow:

- `main` - Production-ready code
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `docs/*` - Documentation changes
- `refactor/*` - Code refactoring

### Creating a Feature Branch

```bash
# Ensure your main branch is up to date
git checkout main
git pull origin main

# Create a new feature branch
git checkout -b feature/your-feature-name
```

### Development Process

1. **Make Changes**
   - Write code following project conventions
   - Add tests for new functionality
   - Update documentation as needed

2. **Test Locally**
   ```bash
   # Run all tests
   pytest tests/
   
   # Run specific test file
   pytest tests/test_specific.py
   
   # Run with coverage
   pytest --cov=src tests/
   ```

3. **Code Quality**
   ```bash
   # Format code (if using black)
   black src/ tests/
   
   # Lint (if using flake8)
   flake8 src/ tests/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Commit Message Convention

We follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Test additions or changes
- `chore` - Maintenance tasks
- `perf` - Performance improvements

**Examples:**
```bash
git commit -m "feat(signals): add RSI trading signal"
git commit -m "fix(api): resolve WebSocket connection timeout"
git commit -m "docs(readme): update installation instructions"
```

---

## Documentation Standards

### Format Requirements

- **File Format**: All documentation must be in Markdown (.md)
- **Code Blocks**: Specify language for syntax highlighting
- **Tables**: Use Markdown tables for structured data
- **Diagrams**: Use Mermaid for architecture diagrams when applicable

### Documentation Structure

Each documentation file should include:

1. **Title**: Clear, descriptive title
**Last Updated:** 2026-08-04
3. **Context Section**: Brief explanation of what the document covers
4. **Sections**: Well-organized with clear headings
5. **Examples**: Practical examples where applicable
6. **Related Links**: Cross-references to related documentation

### Template

```markdown
# Document Title

**Last Updated:** 2026-08-04

## Context

Brief description of what this document covers and why it matters.

## Section 1

Content...

## Section 2

Content...

## Examples

Example code or usage...

## Related Documentation

- [Related Doc 1](path/to/doc1.md)
- [Related Doc 2](path/to/doc2.md)

---

**Last Updated:** 2026-08-04
```

### Documentation Locations

- **Project Root**: README.md, CHANGELOG.md, CONTRIBUTING.md
- **docs/**: Main documentation directory
  - `getting-started/` - Setup and installation guides
  - `core/` - Core system documentation
  - `features/` - Feature-specific documentation
  - `reference/` - Reference materials
  - `knowledge/` - Knowledge base and best practices
- **docs-archive/**: Historical documentation

### Updating Documentation

- Keep documentation in sync with code changes
- Update the docs/INDEX.md when adding new documentation
- Follow existing patterns for consistency
- Include troubleshooting sections where applicable
- Add "Last Updated" field to all documentation files

---

## Code Style Guidelines

### Python Code Style

We follow PEP 8 with some project-specific conventions documented in `docs/knowledge/best-practices/code-conventions.md`.

#### Key Guidelines

1. **Database Queries**
   - Always use parameterized queries
   - Include query timeout settings
   - Log slow queries (>1s)

2. **Error Handling**
   - Don't over-wrap in try/catch
   - Include context in error messages
   - Use specific exception types

3. **Configuration**
   - Never commit secrets or API keys
   - Use environment variables for sensitive data
   - Validate configuration at startup

4. **Testing**
   - Write failing tests first for bug fixes
   - Test edge cases and error conditions
   - Keep tests independent and fast

### Code Organization

- **src/**: Source code directory
  - Organize by feature/module
  - Keep related functionality together
- **tests/**: Test directory
  - Mirror src/ structure
  - Use descriptive test names
- **config/**: Configuration files
  - YAML for structured configuration
  - .env for environment variables

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Variables**: `snake_case`
- **Files**: `snake_case.py`

### Comments and Docstrings

- Use docstrings for all modules, classes, and functions
- Follow Google docstring format
- Add inline comments for complex logic
- Keep comments up to date with code changes

---

## Testing Requirements

### Test Coverage

- Aim for >80% code coverage on new features
- All critical paths must have tests
- Bug fixes must include regression tests

### Test Types

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Test performance characteristics

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_specific.py

# Run specific test function
pytest tests/test_specific.py::test_function_name

# Run with verbose output
pytest -v tests/
```

### Writing Tests

```python
import pytest
from src.module import function_to_test

def test_function_success_case():
    """Test that function handles valid input correctly."""
    result = function_to_test(valid_input)
    assert result == expected_output

def test_function_error_case():
    """Test that function handles invalid input correctly."""
    with pytest.raises(ExpectedException):
        function_to_test(invalid_input)
```

### Test Data

- Use fixtures for test data
- Keep test data minimal but representative
- Clean up test data after tests
- Use in-memory databases when possible

---

## Pull Request Process

### Before Submitting

1. **Code Review Checklist**
   - [ ] Code follows project conventions
   - [ ] Tests pass locally
   - [ ] Documentation is updated
   - [ ] Commit messages follow convention
   - [ ] No sensitive data committed

2. **Self-Review**
   - Review your own changes
   - Ensure code is clean and readable
   - Remove commented-out code
   - Remove debug statements

### Submitting a Pull Request

1. **Push Your Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Go to GitHub and create a PR
   - Use a descriptive title
   - Reference related issues
   - Fill out the PR template

3. **PR Description Template**

   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Related Issues
   Fixes #123
   Related to #456
   
   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   - [ ] Commit messages follow convention
   ```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code quality checks pass
   - Build succeeds

2. **Manual Review**
   - Maintainer reviews your changes
   - Requests changes if needed
   - Approves when ready

3. **Addressing Feedback**
   - Make requested changes
   - Push updates to your branch
   - Request re-review

### Merging

- Squash merge for feature branches
- Maintain clean commit history
- Delete branch after merge
- Update CHANGELOG.md

---

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions

### Getting Help

- Check existing documentation first
- Search existing issues and discussions
- Ask questions in GitHub Discussions
- Be patient with responses

### Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation for major features

---

## Additional Resources

- [Project Documentation](docs/INDEX.md)
- [API Guide](docs/core/API_GUIDE.md)
- [Architecture](docs/core/ARCHITECTURE.md)
- [Code Conventions](docs/knowledge/best-practices/code-conventions.md)
- [Troubleshooting](docs/core/TROUBLESHOOTING.md)

---

**Last Updated:** 2026-08-04