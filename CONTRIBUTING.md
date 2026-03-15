# Contributing to CodeMap

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git

### Setting Up the Development Environment

```bash
# 1. Clone the repository
git clone https://github.com/polprog-tech/CodeMap.git
cd CodeMap

# 2. (Recommended) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Verify the installation
codemap --help
pytest
```

## Development Workflow

### Running Tests

```bash
# All tests
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=codemap --cov-report=term-missing

# Specific test file or class
pytest tests/test_rendering.py
pytest tests/test_rendering.py::TestHtmlRenderer
```

### Linting

```bash
ruff check src/ tests/
ruff format --check src/ tests/

# Auto-fix
ruff check --fix src/ tests/
ruff format src/ tests/
```

### Type Checking

```bash
mypy src/
```

### Run All Checks

```bash
ruff check src/ tests/ && ruff format --check src/ tests/ && mypy src/ && pytest
```

### Testing with Example Projects

```bash
codemap scan   examples/python_project
codemap graph  examples/python_project --no-git
codemap report examples/python_project --no-git
```

## Architecture

Please read [docs/architecture.md](docs/architecture.md) before making changes. Key principles:

1. **Domain layer** (`src/codemap/domain/`) has zero external dependencies
2. **Application layer** orchestrates but does not import infrastructure directly at module level
3. **Infrastructure layer** implements domain contracts (Protocols)
4. **CLI layer** is a thin adapter between user input and application use cases

### Where to Put New Code

| What | Where |
|------|-------|
| New model/value object | `domain/model.py` |
| New metric | `domain/metrics.py` |
| New language extractor | `infrastructure/extractors/` |
| New output format | `rendering/` |
| New CLI command | `cli/commands/` |
| New use case | `application/` |

### Adding a Language Extractor

1. Create a new file in `infrastructure/extractors/` (e.g., `rust_extractor.py`)
2. Implement the `DependencyExtractor` protocol from `domain/model.py`
3. Register in `analyzer.py`'s extractor mapping
4. Write tests in `tests/`

### Adding an Output Format

1. Create a new renderer in `rendering/` implementing `GraphRenderer`
2. Register in `grapher.py`'s format mapping
3. Add CLI flag in `cli/commands/graph.py` if needed
4. Write tests

## Pull Request Process

1. Fork the repository and create a feature branch from `main`
2. Make your changes following the architecture guidelines
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Ensure linting passes: `ruff check src/ tests/`
6. Update documentation if needed
7. Submit a pull request using the PR template

### Commit Messages

Use conventional commit style:

```
feat: add Rust dependency extractor
fix: handle circular imports gracefully
test: add edge case tests for large-graph clustering
docs: update architecture diagram
refactor: extract common analysis logic
```

## Code Style

- Full type hints on all function signatures
- Docstrings on public classes and functions
- Use `from __future__ import annotations` in all modules
- All UI strings go through the `T(key)` I18N function with both `en` and `pl` entries
- All CSS colors use `var(--name)` custom properties for theme support
- Follow existing patterns in the codebase
- Let `ruff` handle formatting

## Reporting Issues

Use the GitHub issue templates:
- **Bug reports** — include reproduction steps, expected vs actual behavior, and environment details
- **Feature requests** — describe the problem, proposed solution, and alternatives considered

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).
