"""Shared pytest fixtures — reusable mini-repositories and graph factories."""

from __future__ import annotations

from pathlib import Path

import pytest

from codemap.domain.model import (
    CodeGraph,
    ContributorInfo,
    Edge,
    EdgeType,
    Language,
    Node,
    NodeGroup,
    NodeMetrics,
    NodeType,
    OwnershipInfo,
)


@pytest.fixture()
def tmp_python_repo(tmp_path: Path) -> Path:
    """Create a minimal Python project under *tmp_path*."""
    pkg = tmp_path / "mylib"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("from mylib.core import hello\n")
    (pkg / "core.py").write_text(
        "from mylib.utils import helper\n\ndef hello():\n    return helper()\n"
    )
    (pkg / "utils.py").write_text("def helper():\n    return 42\n")
    return tmp_path


@pytest.fixture()
def tmp_js_repo(tmp_path: Path) -> Path:
    """Create a minimal JS project under *tmp_path*."""
    src = tmp_path / "src"
    src.mkdir()
    comp = src / "components"
    comp.mkdir()
    utils = src / "utils"
    utils.mkdir()

    (src / "index.js").write_text("import { App } from './components/App.jsx';\nApp();\n")
    (comp / "App.jsx").write_text(
        "import { format } from '../utils/helpers.js';\nexport function App() {}\n"
    )
    (utils / "helpers.js").write_text("export function format(s) { return s; }\n")
    return tmp_path


@pytest.fixture()
def tmp_empty_repo(tmp_path: Path) -> Path:
    """An empty directory — no source files at all."""
    return tmp_path


@pytest.fixture()
def tmp_mixed_repo(tmp_path: Path) -> Path:
    """A directory with both Python and JS files."""
    (tmp_path / "app.py").write_text("import os\nprint('hi')\n")
    (tmp_path / "main.js").write_text("import { x } from './lib.js';\n")
    (tmp_path / "lib.js").write_text("export const x = 1;\n")
    return tmp_path


@pytest.fixture()
def sample_graph() -> CodeGraph:
    """A small hand-built CodeGraph for testing metrics/rendering."""
    graph = CodeGraph(root_path="/repo")

    nodes = [
        Node(
            id="a.py",
            label="a.py",
            node_type=NodeType.FILE,
            file_path="a.py",
            group="",
            language=Language.PYTHON,
            line_count=50,
        ),
        Node(
            id="b.py",
            label="b.py",
            node_type=NodeType.FILE,
            file_path="b.py",
            group="pkg",
            language=Language.PYTHON,
            line_count=100,
        ),
        Node(
            id="c.py",
            label="c.py",
            node_type=NodeType.FILE,
            file_path="c.py",
            group="pkg",
            language=Language.PYTHON,
            line_count=30,
        ),
    ]
    for n in nodes:
        graph.add_node(n)

    graph.add_group(NodeGroup(id="pkg", label="pkg"))

    graph.add_edge(Edge(source="a.py", target="b.py", edge_type=EdgeType.IMPORTS))
    graph.add_edge(Edge(source="a.py", target="c.py", edge_type=EdgeType.IMPORTS))
    graph.add_edge(Edge(source="b.py", target="c.py", edge_type=EdgeType.IMPORTS))

    return graph


@pytest.fixture()
def graph_with_ownership() -> CodeGraph:
    """A graph with ownership metadata attached."""
    graph = CodeGraph(root_path="/repo")

    alice = ContributorInfo(
        name="Alice",
        email="alice@test.com",
        commit_count=10,
        last_commit_date="2026-01-15",
        first_commit_date="2025-06-01",
    )
    bob = ContributorInfo(
        name="Bob",
        email="bob@test.com",
        commit_count=3,
        last_commit_date="2026-01-10",
        first_commit_date="2025-12-01",
    )

    node = Node(
        id="core.py",
        label="core.py",
        node_type=NodeType.FILE,
        file_path="core.py",
        group="",
        language=Language.PYTHON,
        line_count=200,
        ownership=OwnershipInfo(
            contributors=[alice, bob],
            total_commits=13,
            last_modified="2026-01-15",
            last_modifier="Alice",
        ),
        metrics=NodeMetrics(fan_in=5, fan_out=2, centrality=0.5, churn=15),
    )
    graph.add_node(node)
    return graph
