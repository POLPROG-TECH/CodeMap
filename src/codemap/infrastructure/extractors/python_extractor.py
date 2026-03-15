"""Python import dependency extractor."""

from __future__ import annotations

import ast
import os
from pathlib import Path

from codemap.domain.model import Edge, EdgeType


class PythonExtractor:
    """
    Extracts import dependencies from Python source files by parsing
    ``import`` and ``from … import`` statements with the AST module.
    """

    @property
    def supported_extensions(self) -> frozenset[str]:
        return frozenset({".py"})

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".py"

    def extract(self, file_path: Path, content: str, repo_root: Path) -> list[Edge]:
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            return []

        source_id = str(file_path.relative_to(repo_root))
        edges: list[Edge] = []

        for node in ast.walk(tree):
            targets = self._resolve_node(node, file_path, repo_root)
            for target in targets:
                edges.append(Edge(source=source_id, target=target, edge_type=EdgeType.IMPORTS))

        return edges

    # ------------------------------------------------------------------

    def _resolve_node(self, node: ast.AST, file_path: Path, repo_root: Path) -> list[str]:
        if isinstance(node, ast.Import):
            return self._resolve_modules([alias.name for alias in node.names], repo_root)

        if isinstance(node, ast.ImportFrom):
            if node.module is None:
                return []
            base = self._resolve_relative(node.module, node.level, file_path, repo_root)
            if base:
                return [base]
            return self._resolve_modules([node.module], repo_root)

        return []

    def _resolve_modules(self, module_names: list[str], repo_root: Path) -> list[str]:
        results: list[str] = []
        for mod in module_names:
            resolved = self._module_to_file(mod, repo_root)
            if resolved:
                results.append(resolved)
        return results

    def _resolve_relative(
        self, module: str, level: int, file_path: Path, repo_root: Path
    ) -> str | None:
        if level == 0:
            return self._module_to_file(module, repo_root)

        base_dir = file_path.parent
        for _ in range(level - 1):
            base_dir = base_dir.parent

        parts = module.split(".") if module else []
        candidate = base_dir.joinpath(*parts)

        # Try as direct .py file
        py_file = candidate.with_suffix(".py")
        if py_file.exists():
            return str(py_file.relative_to(repo_root))

        # Try as package __init__.py
        init_file = candidate / "__init__.py"
        if init_file.exists():
            return str(init_file.relative_to(repo_root))

        return None

    @staticmethod
    def _module_to_file(module: str, repo_root: Path) -> str | None:
        parts = module.split(".")
        candidate = repo_root.joinpath(*parts)

        py_file = candidate.with_suffix(".py")
        if py_file.exists():
            return str(py_file.relative_to(repo_root))

        init_file = candidate / "__init__.py"
        if init_file.exists():
            return str(init_file.relative_to(repo_root))

        # Also check under common source roots
        for src_dir in ("src", "lib"):
            alt = repo_root / src_dir / os.sep.join(parts)
            py_alt = alt.with_suffix(".py")
            if py_alt.exists():
                return str(py_alt.relative_to(repo_root))
            init_alt = alt / "__init__.py"
            if init_alt.exists():
                return str(init_alt.relative_to(repo_root))

        return None
