"""Tests for dependency extraction (Python and JavaScript extractors)."""

from __future__ import annotations

from pathlib import Path

from codemap.infrastructure.extractors.js_extractor import JavaScriptExtractor
from codemap.infrastructure.extractors.python_extractor import PythonExtractor


class TestPythonExtractor:
    """Tests for Python AST-based import extraction."""

    """GIVEN a Python file that uses `from mylib.utils import helper`"""
    def test_extracts_from_import(self, tmp_python_repo: Path) -> None:
        """WHEN we extract dependencies"""
        extractor = PythonExtractor()
        file_path = tmp_python_repo / "mylib" / "core.py"
        content = file_path.read_text()
        edges = extractor.extract(file_path, content, tmp_python_repo)

        """THEN the import to mylib/utils.py is detected"""
        targets = {e.target for e in edges}
        assert "mylib/utils.py" in targets

    """GIVEN an __init__.py importing from a sibling module"""
    def test_extracts_init_import(self, tmp_python_repo: Path) -> None:
        """WHEN we extract dependencies"""
        extractor = PythonExtractor()
        file_path = tmp_python_repo / "mylib" / "__init__.py"
        content = file_path.read_text()
        edges = extractor.extract(file_path, content, tmp_python_repo)

        """THEN the import to mylib/core.py is detected"""
        targets = {e.target for e in edges}
        assert "mylib/core.py" in targets

    """GIVEN a Python file with invalid syntax"""
    def test_handles_syntax_error(self, tmp_path: Path) -> None:
        """WHEN we extract dependencies"""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def broken(\n")
        extractor = PythonExtractor()
        edges = extractor.extract(bad_file, bad_file.read_text(), tmp_path)

        """THEN no edges are returned (graceful degradation)"""
        assert edges == []

    """GIVEN the Python extractor"""
    def test_can_handle_filters_extensions(self) -> None:
        """WHEN we check supported extensions"""
        extractor = PythonExtractor()

        """THEN only .py files are accepted"""
        assert extractor.can_handle(Path("module.py"))
        assert not extractor.can_handle(Path("module.js"))

    """GIVEN a file importing only standard library modules"""
    def test_ignores_stdlib_imports(self, tmp_path: Path) -> None:
        """WHEN we extract dependencies"""
        f = tmp_path / "app.py"
        f.write_text("import os\nimport sys\nfrom pathlib import Path\n")
        extractor = PythonExtractor()
        edges = extractor.extract(f, f.read_text(), tmp_path)

        """THEN no edges are produced (stdlib has no local file targets)"""
        assert edges == []


class TestJavaScriptExtractor:
    """Tests for regex-based JS/TS import extraction."""

    """GIVEN a JS file with ES module imports"""
    def test_extracts_es_import(self, tmp_js_repo: Path) -> None:
        """WHEN we extract dependencies"""
        extractor = JavaScriptExtractor()
        file_path = tmp_js_repo / "src" / "index.js"
        content = file_path.read_text()
        edges = extractor.extract(file_path, content, tmp_js_repo)

        """THEN the import to App.jsx is resolved"""
        targets = {e.target for e in edges}
        assert "src/components/App.jsx" in targets

    """GIVEN App.jsx importing from ../utils/helpers.js"""
    def test_extracts_relative_import_to_utils(self, tmp_js_repo: Path) -> None:
        """WHEN we extract dependencies"""
        extractor = JavaScriptExtractor()
        file_path = tmp_js_repo / "src" / "components" / "App.jsx"
        content = file_path.read_text()
        edges = extractor.extract(file_path, content, tmp_js_repo)

        """THEN the import to helpers.js is resolved"""
        targets = {e.target for e in edges}
        assert "src/utils/helpers.js" in targets

    """GIVEN a JS file importing an npm package via a bare specifier"""
    def test_ignores_bare_specifiers(self, tmp_path: Path) -> None:
        """WHEN we extract dependencies"""
        f = tmp_path / "app.js"
        f.write_text("import React from 'react';\nimport { useState } from 'react';\n")
        extractor = JavaScriptExtractor()
        edges = extractor.extract(f, f.read_text(), tmp_path)

        """THEN no edges are produced (bare specifiers are not local files)"""
        assert edges == []

    """GIVEN a file using CommonJS require"""
    def test_extracts_require(self, tmp_path: Path) -> None:
        """WHEN we extract dependencies"""
        lib = tmp_path / "lib.js"
        lib.write_text("module.exports = 42;\n")
        f = tmp_path / "app.js"
        f.write_text("const lib = require('./lib.js');\n")
        extractor = JavaScriptExtractor()
        edges = extractor.extract(f, f.read_text(), tmp_path)

        """THEN the required module is resolved as an edge"""
        targets = {e.target for e in edges}
        assert "lib.js" in targets

    """GIVEN the JavaScript extractor"""
    def test_can_handle_filters_extensions(self) -> None:
        """WHEN we check which files it can handle"""
        ext = JavaScriptExtractor()

        """THEN JS/TS/JSX/TSX are accepted and Python is rejected"""
        assert ext.can_handle(Path("app.js"))
        assert ext.can_handle(Path("app.tsx"))
        assert not ext.can_handle(Path("app.py"))
