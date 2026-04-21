"""Repository scanning use-case - discovers files and technologies."""

from __future__ import annotations

from codemap.application.config import CodeMapConfig
from codemap.infrastructure.filesystem import FileScanner, ScanResult


def scan_repository(config: CodeMapConfig) -> ScanResult:
    """Scan the repository at *config.repo_path* and return discovered files."""
    scanner = FileScanner(
        ignored_dirs=config.ignored_dirs,
        supported_extensions=config.supported_extensions,
        include_patterns=config.include_patterns,
        exclude_patterns=config.exclude_patterns,
    )
    return scanner.scan(config.repo_path)
