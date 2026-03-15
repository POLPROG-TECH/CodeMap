"""Protocols (interfaces) defining the extension contracts for CodeMap."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from codemap.domain.model import CodeGraph, Edge, OwnershipInfo


@runtime_checkable
class DependencyExtractor(Protocol):
    """Extracts dependency edges from a single source file."""

    @property
    def supported_extensions(self) -> frozenset[str]: ...

    def can_handle(self, file_path: Path) -> bool: ...

    def extract(self, file_path: Path, content: str, repo_root: Path) -> list[Edge]: ...


@runtime_checkable
class OwnershipProvider(Protocol):
    """Provides contributor / ownership data for files in a repository."""

    def is_available(self) -> bool: ...

    def get_ownership(self, file_path: Path) -> OwnershipInfo: ...

    def get_file_churn(self, file_path: Path) -> int: ...


@runtime_checkable
class GraphRenderer(Protocol):
    """Renders a CodeGraph to an output artifact."""

    @property
    def format_name(self) -> str: ...

    def render(self, graph: CodeGraph, output_path: Path) -> Path: ...
