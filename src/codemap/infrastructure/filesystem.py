"""File-system scanning with configurable include/exclude rules."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

from codemap.domain.model import Language

DEFAULT_IGNORED_DIRS: frozenset[str] = frozenset(
    {
        "node_modules",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        "dist",
        "build",
        ".next",
        ".nuxt",
        "coverage",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".eggs",
        ".idea",
        ".vscode",
    }
)

DEFAULT_SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
)


@dataclass(frozen=True)
class ScannedFile:
    """A single file discovered during repository scanning."""

    path: Path
    relative_path: str
    extension: str
    language: Language
    line_count: int
    size_bytes: int


@dataclass
class ScanResult:
    """Aggregate result of scanning a repository."""

    root: Path
    files: list[ScannedFile] = field(default_factory=list)
    skipped_dirs: list[str] = field(default_factory=list)
    languages_detected: set[Language] = field(default_factory=set)

    @property
    def file_count(self) -> int:
        return len(self.files)


class FileScanner:
    """Walks a repository tree respecting include/exclude rules."""

    def __init__(
        self,
        ignored_dirs: frozenset[str] = DEFAULT_IGNORED_DIRS,
        supported_extensions: frozenset[str] = DEFAULT_SUPPORTED_EXTENSIONS,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> None:
        self._ignored_dirs = ignored_dirs
        self._supported_extensions = supported_extensions
        self._include_patterns = include_patterns or []
        self._exclude_patterns = exclude_patterns or []

    def scan(self, repo_path: Path) -> ScanResult:
        if not repo_path.is_dir():
            raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

        result = ScanResult(root=repo_path.resolve())
        self._walk(repo_path.resolve(), result)
        return result

    # ------------------------------------------------------------------

    def _walk(self, root: Path, result: ScanResult) -> None:
        try:
            entries = sorted(root.iterdir())
        except PermissionError:
            return

        for entry in entries:
            if entry.is_dir():
                if entry.name in self._ignored_dirs or entry.name.startswith("."):
                    result.skipped_dirs.append(str(entry.relative_to(result.root)))
                    continue
                self._walk(entry, result)
            elif entry.is_file():
                self._process_file(entry, result)

    def _process_file(self, path: Path, result: ScanResult) -> None:
        ext = path.suffix.lower()
        if ext not in self._supported_extensions:
            return

        rel = str(path.relative_to(result.root))

        if self._exclude_patterns and any(fnmatch.fnmatch(rel, p) for p in self._exclude_patterns):
            return

        if self._include_patterns and not any(
            fnmatch.fnmatch(rel, p) for p in self._include_patterns
        ):
            return

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            line_count = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
        except OSError:
            line_count = 0

        language = Language.from_extension(ext)

        scanned = ScannedFile(
            path=path,
            relative_path=rel,
            extension=ext,
            language=language,
            line_count=line_count,
            size_bytes=path.stat().st_size,
        )
        result.files.append(scanned)
        result.languages_detected.add(language)
