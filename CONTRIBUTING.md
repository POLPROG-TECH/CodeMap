# Contributing to CodeMap

Thank you for your interest in contributing to CodeMap! This guide covers everything you need to get started.

## Development Setup

```bash
git clone https://github.com/polprog-tech/CodeMap.git
cd CodeMap

python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -e ".[dev]"
```

Verify the installation:

```bash
codemap --help
```

### Pre-commit hook

```bash
cp scripts/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

## Running Tests

```bash
pytest                                    # all tests
pytest -v                                 # verbose
pytest tests/test_rendering_html.py       # specific file
pytest tests/test_rendering_html.py::TestHtmlRenderer  # specific class
pytest --cov=codemap --cov-report=term-missing         # with coverage
```

Tests follow the **GIVEN/WHEN/THEN** docstring pattern (see existing tests for examples).

## Code Quality

```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/codemap/ --ignore-missing-imports
```

Auto-fix:

```bash
ruff check --fix src/ tests/
ruff format src/ tests/
```

## How to Contribute

### Reporting Bugs

Include: expected vs actual behavior, command used, Python/OS version, and steps to reproduce.

### Pull Requests

1. Branch from `main`
2. Make changes and add tests
3. Run `pytest` and `ruff check src/ tests/`
4. Open a PR with a clear description

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

## Commit Convention

[Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`

## License

See [LICENSE](LICENSE).
