"""JavaScript / TypeScript import dependency extractor."""

from __future__ import annotations

import re
from pathlib import Path

from codemap.domain.model import Edge, EdgeType

# Patterns for ES module imports and CommonJS require
_ES_IMPORT_RE = re.compile(
    r"""(?:import\s+(?:[\w{},*\s]+\s+from\s+)?|export\s+(?:[\w{},*\s]+\s+from\s+)?)['"]([^'"]+)['"]""",
)
_REQUIRE_RE = re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""")

_JS_EXTENSIONS: frozenset[str] = frozenset({".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"})
_RESOLVE_EXTENSIONS: tuple[str, ...] = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")


class JavaScriptExtractor:
    """
    Extracts import/require dependencies from JS/TS source files
    using regex-based heuristic parsing.
    """

    @property
    def supported_extensions(self) -> frozenset[str]:
        return _JS_EXTENSIONS

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in _JS_EXTENSIONS

    def extract(self, file_path: Path, content: str, repo_root: Path) -> list[Edge]:
        source_id = str(file_path.relative_to(repo_root))
        raw_imports = self._find_imports(content)
        edges: list[Edge] = []

        for imp in raw_imports:
            if not imp.startswith("."):
                continue  # skip bare specifiers (npm packages)
            resolved = self._resolve(imp, file_path, repo_root)
            if resolved:
                edges.append(Edge(source=source_id, target=resolved, edge_type=EdgeType.IMPORTS))

        return edges

    # ------------------------------------------------------------------

    @staticmethod
    def _find_imports(content: str) -> list[str]:
        imports: list[str] = []
        for match in _ES_IMPORT_RE.finditer(content):
            imports.append(match.group(1))
        for match in _REQUIRE_RE.finditer(content):
            imports.append(match.group(1))
        return imports

    @staticmethod
    def _resolve(specifier: str, from_file: Path, repo_root: Path) -> str | None:
        base = from_file.parent / specifier

        # Exact file
        if base.is_file():
            return str(base.resolve().relative_to(repo_root.resolve()))

        # Try common extensions
        for ext in _RESOLVE_EXTENSIONS:
            candidate = base.with_suffix(ext)
            if candidate.is_file():
                return str(candidate.resolve().relative_to(repo_root.resolve()))

        # Try index files in a directory
        if base.is_dir():
            for ext in _RESOLVE_EXTENSIONS:
                index = base / f"index{ext}"
                if index.is_file():
                    return str(index.resolve().relative_to(repo_root.resolve()))

        return None
