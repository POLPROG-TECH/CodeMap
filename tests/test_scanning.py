"""Tests for repository scanning (FileScanner)."""

from __future__ import annotations

from pathlib import Path

import pytest

from codemap.domain.model import Language
from codemap.infrastructure.filesystem import FileScanner


class TestFileScannerBasicDiscovery:
    """Scanning a directory discovers files and respects extension filters."""

    def test_discovers_python_files(self, tmp_python_repo: Path) -> None:
        # GIVEN a directory containing .py files
        scanner = FileScanner()

        # WHEN we scan the directory
        result = scanner.scan(tmp_python_repo)

        # THEN all Python files are discovered
        paths = {f.relative_path for f in result.files}
        assert "mylib/__init__.py" in paths
        assert "mylib/core.py" in paths
        assert "mylib/utils.py" in paths

    def test_discovers_javascript_files(self, tmp_js_repo: Path) -> None:
        # GIVEN a directory containing .js and .jsx files
        scanner = FileScanner()

        # WHEN we scan the directory
        result = scanner.scan(tmp_js_repo)

        # THEN all JS/JSX files are discovered
        paths = {f.relative_path for f in result.files}
        assert "src/index.js" in paths
        assert "src/components/App.jsx" in paths
        assert "src/utils/helpers.js" in paths

    def test_detects_languages(self, tmp_mixed_repo: Path) -> None:
        # GIVEN a directory with both Python and JavaScript files
        scanner = FileScanner()

        # WHEN we scan the directory
        result = scanner.scan(tmp_mixed_repo)

        # THEN both languages are detected
        assert Language.PYTHON in result.languages_detected
        assert Language.JAVASCRIPT in result.languages_detected

    def test_counts_lines(self, tmp_python_repo: Path) -> None:
        # GIVEN a Python file with known content
        scanner = FileScanner()

        # WHEN we scan the directory
        result = scanner.scan(tmp_python_repo)

        # THEN line counts are populated and positive
        for f in result.files:
            assert f.line_count > 0


class TestFileScannerEmptyRepo:
    """Scanning an empty repository returns an empty result."""

    def test_empty_directory(self, tmp_empty_repo: Path) -> None:
        # GIVEN an empty directory
        scanner = FileScanner()

        # WHEN we scan it
        result = scanner.scan(tmp_empty_repo)

        # THEN no files are found
        assert result.file_count == 0
        assert result.languages_detected == set()


class TestFileScannerNonExistentPath:
    """Scanning a path that does not exist raises an error."""

    def test_raises_file_not_found(self, tmp_path: Path) -> None:
        # GIVEN a path that does not exist
        bad_path = tmp_path / "does_not_exist"
        scanner = FileScanner()

        # WHEN we attempt to scan it
        # THEN FileNotFoundError is raised
        with pytest.raises(FileNotFoundError):
            scanner.scan(bad_path)


class TestFileScannerIncludeExclude:
    """Include and exclude glob patterns are applied correctly."""

    def test_exclude_pattern(self, tmp_python_repo: Path) -> None:
        # GIVEN a scanner configured to exclude __init__.py
        scanner = FileScanner(exclude_patterns=["*/__init__.py"])

        # WHEN we scan
        result = scanner.scan(tmp_python_repo)

        # THEN __init__.py is not included
        paths = {f.relative_path for f in result.files}
        assert "mylib/__init__.py" not in paths
        assert "mylib/core.py" in paths

    def test_include_pattern(self, tmp_python_repo: Path) -> None:
        # GIVEN a scanner configured to include only core.py
        scanner = FileScanner(include_patterns=["*/core.py"])

        # WHEN we scan
        result = scanner.scan(tmp_python_repo)

        # THEN only core.py is included
        assert result.file_count == 1
        assert result.files[0].relative_path == "mylib/core.py"


class TestFileScannerIgnoredDirectories:
    """Known noisy directories are skipped automatically."""

    def test_ignores_node_modules(self, tmp_path: Path) -> None:
        # GIVEN a project with a node_modules directory
        nm = tmp_path / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("module.exports = 1;\n")
        (tmp_path / "app.js").write_text("const x = 1;\n")
        scanner = FileScanner()

        # WHEN we scan
        result = scanner.scan(tmp_path)

        # THEN node_modules content is excluded
        paths = {f.relative_path for f in result.files}
        assert "app.js" in paths
        assert "node_modules/pkg/index.js" not in paths

    def test_ignores_pycache(self, tmp_path: Path) -> None:
        # GIVEN a project with __pycache__
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "mod.cpython-312.pyc").write_text("")
        (tmp_path / "mod.py").write_text("x = 1\n")
        scanner = FileScanner()

        # WHEN we scan
        result = scanner.scan(tmp_path)

        # THEN __pycache__ is skipped (and .pyc isn't a supported extension anyway)
        paths = {f.relative_path for f in result.files}
        assert "mod.py" in paths
        assert len(paths) == 1
