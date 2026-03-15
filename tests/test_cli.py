"""Tests for CLI commands — happy paths and failure modes."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from codemap.cli.app import app

runner = CliRunner()


class TestScanCommand:
    """The ``scan`` CLI command."""

    def test_scan_python_repo(self, tmp_python_repo: Path) -> None:
        # GIVEN a directory with Python files
        # WHEN we run `codemap scan <path>`
        result = runner.invoke(app, ["scan", str(tmp_python_repo)])

        # THEN exit code is 0 and output lists discovered files
        assert result.exit_code == 0
        assert "core.py" in result.output
        assert "utils.py" in result.output

    def test_scan_js_repo(self, tmp_js_repo: Path) -> None:
        # GIVEN a directory with JS files
        # WHEN we run `codemap scan <path>`
        result = runner.invoke(app, ["scan", str(tmp_js_repo)])

        # THEN exit code is 0 and JS files appear
        assert result.exit_code == 0
        assert "index.js" in result.output
        assert "App.jsx" in result.output

    def test_scan_nonexistent_path(self, tmp_path: Path) -> None:
        # GIVEN a path that does not exist
        bad_path = str(tmp_path / "no_such_dir")

        # WHEN we run `codemap scan <bad_path>`
        result = runner.invoke(app, ["scan", bad_path])

        # THEN exit code is 1 and error message is shown
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_scan_empty_repo(self, tmp_empty_repo: Path) -> None:
        # GIVEN an empty directory
        # WHEN we run `codemap scan <path>`
        result = runner.invoke(app, ["scan", str(tmp_empty_repo)])

        # THEN exit code is 0 (no crash) and file count is 0
        assert result.exit_code == 0
        assert "0 files" in result.output


class TestAnalyzeCommand:
    """The ``analyze`` CLI command."""

    def test_analyze_with_no_git(self, tmp_python_repo: Path) -> None:
        # GIVEN a Python repo without git
        # WHEN we run `codemap analyze --no-git`
        result = runner.invoke(app, ["analyze", str(tmp_python_repo), "--no-git"])

        # THEN exit code is 0 and output shows node/edge counts
        assert result.exit_code == 0
        assert "Nodes:" in result.output
        assert "Edges:" in result.output


class TestGraphCommand:
    """The ``graph`` CLI command."""

    def test_graph_html_output(self, tmp_js_repo: Path, tmp_path: Path) -> None:
        # GIVEN a JS repo
        out_dir = tmp_path / "output"

        # WHEN we run `codemap graph --no-git -o <out_dir>`
        result = runner.invoke(app, ["graph", str(tmp_js_repo), "--no-git", "-o", str(out_dir)])

        # THEN exit code is 0 and an HTML file is created
        assert result.exit_code == 0
        assert (out_dir / "codemap.html").exists()

    def test_graph_json_output(self, tmp_python_repo: Path, tmp_path: Path) -> None:
        # GIVEN a Python repo
        out_dir = tmp_path / "output"

        # WHEN we run `codemap graph --no-git -f json`
        result = runner.invoke(
            app, ["graph", str(tmp_python_repo), "--no-git", "-f", "json", "-o", str(out_dir)]
        )

        # THEN exit code is 0 and a JSON file is created
        assert result.exit_code == 0
        assert (out_dir / "codemap.json").exists()

    def test_graph_pdf_output(self, tmp_python_repo: Path, tmp_path: Path) -> None:
        # GIVEN a Python repo
        out_dir = tmp_path / "output"

        # WHEN we run `codemap graph --no-git -f pdf`
        result = runner.invoke(
            app, ["graph", str(tmp_python_repo), "--no-git", "-f", "pdf", "-o", str(out_dir)]
        )

        # THEN exit code is 0 and a PDF file is created
        assert result.exit_code == 0
        pdf_file = out_dir / "codemap.pdf"
        assert pdf_file.exists()
        assert pdf_file.read_bytes()[:5] == b"%PDF-"


class TestReportCommand:
    """The ``report`` CLI command."""

    def test_report_terminal_output(self, tmp_python_repo: Path) -> None:
        # GIVEN a Python repo
        # WHEN we run `codemap report --no-git`
        result = runner.invoke(app, ["report", str(tmp_python_repo), "--no-git"])

        # THEN exit code is 0 and report headers appear
        assert result.exit_code == 0
        assert "CodeMap Report" in result.output

    def test_report_with_json(self, tmp_python_repo: Path, tmp_path: Path) -> None:
        # GIVEN a Python repo
        out_dir = tmp_path / "output"

        # WHEN we run `codemap report --no-git --json`
        result = runner.invoke(
            app, ["report", str(tmp_python_repo), "--no-git", "--json", "-o", str(out_dir)]
        )

        # THEN exit code is 0 and JSON report file is created
        assert result.exit_code == 0
        assert (out_dir / "codemap_report.json").exists()


class TestProgressReporting:
    """CLI commands show progress stages."""

    def test_analyze_shows_stage_labels(self, tmp_python_repo: Path) -> None:
        # GIVEN a Python repo
        # WHEN we run `codemap analyze --no-git`
        result = runner.invoke(app, ["analyze", str(tmp_python_repo), "--no-git"])

        # THEN progress stage labels appear in output
        assert result.exit_code == 0
        assert "Scanned" in result.output
        assert "Building node graph" in result.output or "Nodes" in result.output

    def test_graph_shows_rendering_stage(self, tmp_python_repo: Path, tmp_path: Path) -> None:
        # GIVEN a Python repo
        out_dir = tmp_path / "output"

        # WHEN we run `codemap graph --no-git`
        result = runner.invoke(app, ["graph", str(tmp_python_repo), "--no-git", "-o", str(out_dir)])

        # THEN rendering stage and output path appear
        assert result.exit_code == 0
        assert "Rendering" in result.output or "Output written to" in result.output

    def test_report_shows_progress(self, tmp_python_repo: Path) -> None:
        # GIVEN a Python repo
        # WHEN we run `codemap report --no-git`
        result = runner.invoke(app, ["report", str(tmp_python_repo), "--no-git"])

        # THEN progress is visible
        assert result.exit_code == 0
        assert "Scanned" in result.output or "CodeMap Report" in result.output

    # ------------------------------------------------------------------
    # --fast flag
    # ------------------------------------------------------------------
    def test_analyze_fast_flag(self, tmp_python_repo: Path) -> None:
        """The --fast flag skips git analysis and still succeeds."""
        result = runner.invoke(app, ["analyze", str(tmp_python_repo), "--fast"])
        assert result.exit_code == 0
        assert "Nodes" in result.output or "Scanned" in result.output

    def test_graph_fast_flag(self, tmp_python_repo: Path) -> None:
        """The --fast flag produces HTML output without git analysis."""
        result = runner.invoke(app, ["graph", str(tmp_python_repo), "--fast", "--no-git"])
        assert result.exit_code == 0
        assert "Output written" in result.output or "codemap" in result.output
