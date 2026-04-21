"""Centralised configuration for a CodeMap analysis run."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from codemap.infrastructure.filesystem import DEFAULT_IGNORED_DIRS, DEFAULT_SUPPORTED_EXTENSIONS


@dataclass
class CodeMapConfig:
    """All tunables for a single CodeMap invocation."""

    repo_path: Path = field(default_factory=lambda: Path("."))
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    ignored_dirs: frozenset[str] = DEFAULT_IGNORED_DIRS
    supported_extensions: frozenset[str] = DEFAULT_SUPPORTED_EXTENSIONS
    enable_git: bool = True
    max_git_commits: int = 1000
    output_dir: Path = field(default_factory=lambda: Path("codemap_output"))
    grouping_mode: str = "directory"
    hotspot_churn_threshold: int = 10
    hotspot_fanin_threshold: int = 3
    # Performance - large-project node threshold for collapsed/progressive view
    large_graph_threshold: int = 200
