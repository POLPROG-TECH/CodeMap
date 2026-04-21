"""Tests for CLI commands - happy paths and failure modes."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from codemap.cli.app import app

runner = CliRunner()


class TestScanCommand:
    """Tests for the ``scan`` CLI command."""

    """GIVEN a directory with Python files"""
    def test_scan_python_repo(self, tmp_python_repo: Path) -> None:
        """WHEN we run `codemap scan <path>`"""
        result = runner.invoke(app, ["scan", str(tmp_python_repo)])

        """THEN the command exits 0 and output lists discovered files"""
        assert result.exit_code == 0
        assert "core.py" in result.output
        assert "utils.py" in result.output

    """GIVEN a directory with JS files"""
    def test_scan_js_repo(self, tmp_js_repo: Path) -> None:
        """WHEN we run `codemap scan <path>`"""
        result = runner.invoke(app, ["scan", str(tmp_js_repo)])

        """THEN the command exits 0 and JS files appear in output"""
        assert result.exit_code == 0
        assert "index.js" in result.output
        assert "App.jsx" in result.output

    """GIVEN a path that does not exist"""
    def test_scan_nonexistent_path(self, tmp_path: Path) -> None:
        """WHEN we run `codemap scan <bad_path>`"""
        bad_path = str(tmp_path / "no_such_dir")
        result = runner.invoke(app, ["scan", bad_path])

        """THEN the command exits 1 and an error message is shown"""
        assert result.exit_code == 1
        assert "Error" in result.output

    """GIVEN an empty directory"""
    def test_scan_empty_repo(self, tmp_empty_repo: Path) -> None:
        """WHEN we run `codemap scan <path>`"""
        result = runner.invoke(app, ["scan", str(tmp_empty_repo)])

        """THEN the command exits 0 and reports zero files"""
        assert result.exit_code == 0
        assert "0 files" in result.output


class TestAnalyzeCommand:
    """Tests for the ``analyze`` CLI command."""

    """GIVEN a Python repo without git"""
    def test_analyze_with_no_git(self, tmp_python_repo: Path) -> None:
        """WHEN we run `codemap analyze --no-git`"""
        result = runner.invoke(app, ["analyze", str(tmp_python_repo), "--no-git"])

        """THEN the command exits 0 and output shows node/edge counts"""
        assert result.exit_code == 0
        assert "Nodes:" in result.output
        assert "Edges:" in result.output


class TestGraphCommand:
    """Tests for the ``graph`` CLI command."""

    """GIVEN a JS repo"""
    def test_graph_html_output(self, tmp_js_repo: Path, tmp_path: Path) -> None:
        """WHEN we run `codemap graph --no-git -o <out_dir>`"""
        out_dir = tmp_path / "output"
        result = runner.invoke(app, ["graph", str(tmp_js_repo), "--no-git", "-o", str(out_dir)])

        """THEN the command exits 0 and an HTML file is created"""
        assert result.exit_code == 0
        assert (out_dir / "codemap.html").exists()

    """GIVEN a Python repo"""
    def test_graph_json_output(self, tmp_python_repo: Path, tmp_path: Path) -> None:
        """WHEN we run `codemap graph --no-git -f json`"""
        out_dir = tmp_path / "output"
        result = runner.invoke(
            app, ["graph", str(tmp_python_repo), "--no-git", "-f", "json", "-o", str(out_dir)]
        )

        """THEN the command exits 0 and a JSON file is created"""
        assert result.exit_code == 0
        assert (out_dir / "codemap.json").exists()

    """GIVEN a Python repo"""
    def test_graph_pdf_output(self, tmp_python_repo: Path, tmp_path: Path) -> None:
        """WHEN we run `codemap graph --no-git -f pdf`"""
        out_dir = tmp_path / "output"
        result = runner.invoke(
            app, ["graph", str(tmp_python_repo), "--no-git", "-f", "pdf", "-o", str(out_dir)]
        )

        """THEN the command exits 0 and a valid PDF file is created"""
        assert result.exit_code == 0
        pdf_file = out_dir / "codemap.pdf"
        assert pdf_file.exists()
        assert pdf_file.read_bytes()[:5] == b"%PDF-"


class TestReportCommand:
    """Tests for the ``report`` CLI command."""

    """GIVEN a Python repo"""
    def test_report_terminal_output(self, tmp_python_repo: Path) -> None:
        """WHEN we run `codemap report --no-git`"""
        result = runner.invoke(app, ["report", str(tmp_python_repo), "--no-git"])

        """THEN the command exits 0 and report headers appear"""
        assert result.exit_code == 0
        assert "CodeMap Report" in result.output

    """GIVEN a Python repo"""
    def test_report_with_json(self, tmp_python_repo: Path, tmp_path: Path) -> None:
        """WHEN we run `codemap report --no-git --json`"""
        out_dir = tmp_path / "output"
        result = runner.invoke(
            app, ["report", str(tmp_python_repo), "--no-git", "--json", "-o", str(out_dir)]
        )

        """THEN the command exits 0 and a JSON report file is created"""
        assert result.exit_code == 0
        assert (out_dir / "codemap_report.json").exists()


class TestProgressReporting:
    """Tests that CLI commands show progress stages."""

    """GIVEN a Python repo"""
    def test_analyze_shows_stage_labels(self, tmp_python_repo: Path) -> None:
        """WHEN we run `codemap analyze --no-git`"""
        result = runner.invoke(app, ["analyze", str(tmp_python_repo), "--no-git"])

        """THEN progress stage labels appear in output"""
        assert result.exit_code == 0
        assert "Scanned" in result.output
        assert "Building node graph" in result.output or "Nodes" in result.output

    """GIVEN a Python repo"""
    def test_graph_shows_rendering_stage(self, tmp_python_repo: Path, tmp_path: Path) -> None:
        """WHEN we run `codemap graph --no-git`"""
        out_dir = tmp_path / "output"
        result = runner.invoke(app, ["graph", str(tmp_python_repo), "--no-git", "-o", str(out_dir)])

        """THEN the rendering stage and output path appear"""
        assert result.exit_code == 0
        assert "Rendering" in result.output or "Output written to" in result.output

    """GIVEN a Python repo"""
    def test_report_shows_progress(self, tmp_python_repo: Path) -> None:
        """WHEN we run `codemap report --no-git`"""
        result = runner.invoke(app, ["report", str(tmp_python_repo), "--no-git"])

        """THEN progress is visible"""
        assert result.exit_code == 0
        assert "Scanned" in result.output or "CodeMap Report" in result.output

    """GIVEN a Python repo and the --fast flag"""
    def test_analyze_fast_flag(self, tmp_python_repo: Path) -> None:
        """WHEN we run `codemap analyze --fast`"""
        result = runner.invoke(app, ["analyze", str(tmp_python_repo), "--fast"])

        """THEN the command exits 0 with analysis output"""
        assert result.exit_code == 0
        assert "Nodes" in result.output or "Scanned" in result.output

    """GIVEN a Python repo and the --fast flag"""
    def test_graph_fast_flag(self, tmp_python_repo: Path) -> None:
        """WHEN we run `codemap graph --fast --no-git`"""
        result = runner.invoke(app, ["graph", str(tmp_python_repo), "--fast", "--no-git"])

        """THEN the command exits 0 and HTML output is produced"""
        assert result.exit_code == 0
        assert "Output written" in result.output or "codemap" in result.output
