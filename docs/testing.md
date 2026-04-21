# Testing

CodeMap uses **pytest** with a GIVEN / WHEN / THEN structure for clarity.

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=codemap --cov-report=term-missing

# Specific test file
python -m pytest tests/test_scanning.py -v
```

## Test Structure

Tests are organized by layer:

| File | Coverage |
|------|----------|
| `test_scanning.py` | FileScanner - discovery, include/exclude, ignored dirs |
| `test_extraction.py` | Python and JS dependency extractors |
| `test_graph.py` | CodeGraph - nodes, edges, groups, queries |
| `test_reverse_deps.py` | Reverse dependency and impact analysis |
| `test_metrics.py` | Fan-in/out, centrality, hotspot detection |
| `test_ownership.py` | OwnershipInfo model, graph attachment |
| `test_rendering.py` | JSON, HTML, and terminal renderer output |
| `test_cli.py` | All CLI commands - happy paths and errors |
| `test_analysis.py` | Full pipeline, grouping, report generation, git absence |

## GIVEN / WHEN / THEN

All tests follow this visible structure:

```python
def test_example(self) -> None:
    # GIVEN some precondition
    graph = CodeGraph()
    graph.add_node(...)

    # WHEN some action is performed
    result = graph.get_dependencies("a.py")

    # THEN expected outcome is verified
    assert len(result) == 2
```

## Fixtures

Shared fixtures are in `tests/conftest.py`:

- `tmp_python_repo` - minimal Python package with imports
- `tmp_js_repo` - minimal JS project with ES imports
- `tmp_empty_repo` - empty directory
- `tmp_mixed_repo` - Python + JS files
- `sample_graph` - hand-built CodeGraph for unit tests
- `graph_with_ownership` - graph with contributor metadata
