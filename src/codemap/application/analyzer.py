"""Analysis use-case - builds the CodeGraph from scan results."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from codemap.application.config import CodeMapConfig
from codemap.domain.metrics import compute_all_metrics
from codemap.domain.model import (
    CodeGraph,
    Node,
    NodeGroup,
    NodeType,
)
from codemap.infrastructure.extractors.js_extractor import JavaScriptExtractor
from codemap.infrastructure.extractors.python_extractor import PythonExtractor
from codemap.infrastructure.filesystem import ScannedFile, ScanResult
from codemap.infrastructure.git import GitAnalyzer


def analyze(
    scan_result: ScanResult,
    config: CodeMapConfig,
    on_stage: Callable[[str], None] | None = None,
    on_file_progress: Callable[[int, int], None] | None = None,
) -> CodeGraph:
    """
    Build a fully-enriched CodeGraph from a ScanResult.

    Args:
        scan_result: Scanned repository files.
        config: Analysis configuration.
        on_stage: Callback invoked with a human-readable stage label.
        on_file_progress: Callback invoked with (current, total) during file processing.

    Steps:
        1. Create nodes for every scanned file.
        2. Create directory groups.
        3. Extract dependency edges.
        4. Enrich with git ownership/churn (if available).
        5. Compute metrics (fan-in, fan-out, centrality).
    """

    def _stage(label: str) -> None:
        if on_stage:
            on_stage(label)

    graph = CodeGraph(root_path=str(scan_result.root))

    # 1. Nodes
    _stage("Building node graph…")
    for sf in scan_result.files:
        _add_file_node(graph, sf)

    # 2. Groups
    _stage("Building directory groups…")
    _build_groups(graph)

    # 3. Dependencies
    _stage("Extracting dependencies…")
    extractors: list[PythonExtractor | JavaScriptExtractor] = [
        PythonExtractor(),
        JavaScriptExtractor(),
    ]
    repo_root = scan_result.root
    total = len(scan_result.files)

    for i, sf in enumerate(scan_result.files):
        for ext in extractors:
            if ext.can_handle(sf.path):
                content = sf.path.read_text(encoding="utf-8", errors="replace")
                for edge in ext.extract(sf.path, content, repo_root):
                    graph.add_edge(edge)
                break  # one extractor per file
        if on_file_progress and (i + 1) % 100 == 0:
            on_file_progress(i + 1, total)
    if on_file_progress:
        on_file_progress(total, total)

    # 4. Git enrichment (batch)
    _stage("Analyzing git ownership…")
    _enrich_ownership(graph, repo_root, config)

    # 5. Metrics
    _stage("Computing metrics…")
    compute_all_metrics(graph)

    return graph


# -- helpers ---------------------------------------------------------------


def _add_file_node(graph: CodeGraph, sf: ScannedFile) -> None:
    parts = Path(sf.relative_path).parts
    group = str(Path(*parts[:-1])) if len(parts) > 1 else ""

    graph.add_node(
        Node(
            id=sf.relative_path,
            label=Path(sf.relative_path).name,
            node_type=NodeType.FILE,
            file_path=sf.relative_path,
            group=group,
            language=sf.language,
            line_count=sf.line_count,
        )
    )


def _build_groups(graph: CodeGraph) -> None:
    seen: set[str] = set()
    for node in list(graph.nodes.values()):
        parts = Path(node.file_path).parts[:-1]
        for i in range(1, len(parts) + 1):
            gid = str(Path(*parts[:i]))
            if gid not in seen:
                parent = str(Path(*parts[: i - 1])) if i > 1 else None
                graph.add_group(NodeGroup(id=gid, label=parts[i - 1], parent=parent))
                seen.add(gid)


def _enrich_ownership(graph: CodeGraph, repo_root: Path, config: CodeMapConfig) -> None:
    if not config.enable_git:
        return

    git = GitAnalyzer(repo_root, max_commits=config.max_git_commits)
    if not git.is_available():
        return

    # Batch prefetch: 2 git calls instead of 2×N
    file_paths = [n.file_path for n in graph.nodes.values()]
    git.prefetch(file_paths)

    for node in graph.nodes.values():
        file_path = repo_root / node.file_path
        node.ownership = git.get_ownership(file_path)
        node.metrics.churn = git.get_file_churn(file_path)
