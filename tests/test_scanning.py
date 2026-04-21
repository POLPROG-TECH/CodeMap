"""Tests for repository scanning (FileScanner)."""

from __future__ import annotations

from pathlib import Path

import pytest

from codemap.domain.model import Language
from codemap.infrastructure.filesystem import FileScanner


class TestFileScannerBasicDiscovery:
    """Tests that scanning discovers files and respects extension filters."""

    """GIVEN a directory containing .py files"""
    def test_discovers_python_files(self, tmp_python_repo: Path) -> None:
        """WHEN we scan the directory"""
        scanner = FileScanner()
        result = scanner.scan(tmp_python_repo)

        """THEN all Python files are discovered"""
        paths = {f.relative_path for f in result.files}
        assert "mylib/__init__.py" in paths
        assert "mylib/core.py" in paths
        assert "mylib/utils.py" in paths

    """GIVEN a directory containing .js and .jsx files"""
    def test_discovers_javascript_files(self, tmp_js_repo: Path) -> None:
        """WHEN we scan the directory"""
        scanner = FileScanner()
        result = scanner.scan(tmp_js_repo)

        """THEN all JS/JSX files are discovered"""
        paths = {f.relative_path for f in result.files}
        assert "src/index.js" in paths
        assert "src/components/App.jsx" in paths
        assert "src/utils/helpers.js" in paths

    """GIVEN a directory with both Python and JavaScript files"""
    def test_detects_languages(self, tmp_mixed_repo: Path) -> None:
        """WHEN we scan the directory"""
        scanner = FileScanner()
        result = scanner.scan(tmp_mixed_repo)

        """THEN both languages are detected"""
        assert Language.PYTHON in result.languages_detected
        assert Language.JAVASCRIPT in result.languages_detected

    """GIVEN a Python file with known content"""
    def test_counts_lines(self, tmp_python_repo: Path) -> None:
        """WHEN we scan the directory"""
        scanner = FileScanner()
        result = scanner.scan(tmp_python_repo)

        """THEN line counts are populated and positive"""
        for f in result.files:
            assert f.line_count > 0


class TestFileScannerEmptyRepo:
    """Tests that scanning an empty repository returns an empty result."""

    """GIVEN an empty directory"""
    def test_empty_directory(self, tmp_empty_repo: Path) -> None:
        """WHEN we scan it"""
        scanner = FileScanner()
        result = scanner.scan(tmp_empty_repo)

        """THEN no files are found"""
        assert result.file_count == 0
        assert result.languages_detected == set()


class TestFileScannerNonExistentPath:
    """Tests that scanning a non-existent path raises an error."""

    """GIVEN a path that does not exist"""
    def test_raises_file_not_found(self, tmp_path: Path) -> None:
        """WHEN we attempt to scan it"""
        bad_path = tmp_path / "does_not_exist"
        scanner = FileScanner()

        """THEN FileNotFoundError is raised"""
        with pytest.raises(FileNotFoundError):
            scanner.scan(bad_path)


class TestFileScannerIncludeExclude:
    """Tests that include and exclude glob patterns are applied correctly."""

    """GIVEN a scanner configured to exclude __init__.py"""
    def test_exclude_pattern(self, tmp_python_repo: Path) -> None:
        """WHEN we scan the directory"""
        scanner = FileScanner(exclude_patterns=["*/__init__.py"])
        result = scanner.scan(tmp_python_repo)

        """THEN __init__.py is not included"""
        paths = {f.relative_path for f in result.files}
        assert "mylib/__init__.py" not in paths
        assert "mylib/core.py" in paths

    """GIVEN a scanner configured to include only core.py"""
    def test_include_pattern(self, tmp_python_repo: Path) -> None:
        """WHEN we scan the directory"""
        scanner = FileScanner(include_patterns=["*/core.py"])
        result = scanner.scan(tmp_python_repo)

        """THEN only core.py is included"""
        assert result.file_count == 1
        assert result.files[0].relative_path == "mylib/core.py"


class TestFileScannerIgnoredDirectories:
    """Tests that known noisy directories are skipped automatically."""

    """GIVEN a project with a node_modules directory"""
    def test_ignores_node_modules(self, tmp_path: Path) -> None:
        """WHEN we scan the directory"""
        nm = tmp_path / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("module.exports = 1;\n")
        (tmp_path / "app.js").write_text("const x = 1;\n")
        scanner = FileScanner()
        result = scanner.scan(tmp_path)

        """THEN node_modules content is excluded"""
        paths = {f.relative_path for f in result.files}
        assert "app.js" in paths
        assert "node_modules/pkg/index.js" not in paths

    """GIVEN a project with __pycache__"""
    def test_ignores_pycache(self, tmp_path: Path) -> None:
        """WHEN we scan the directory"""
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "mod.cpython-312.pyc").write_text("")
        (tmp_path / "mod.py").write_text("x = 1\n")
        scanner = FileScanner()
        result = scanner.scan(tmp_path)

        """THEN __pycache__ is skipped and .pyc files are not collected"""
        paths = {f.relative_path for f in result.files}
        assert "mod.py" in paths
        assert len(paths) == 1
