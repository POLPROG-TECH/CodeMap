"""Tests for the full analysis pipeline and grouping/hierarchy logic."""

from __future__ import annotations

from pathlib import Path

from codemap.application.analyzer import analyze
from codemap.application.config import CodeMapConfig
from codemap.application.reporter import generate_report
from codemap.application.scanner import scan_repository


class TestAnalysisPipeline:
    """End-to-end analysis pipeline integration tests."""

    """GIVEN a Python project with inter-module imports"""
    def test_python_project_produces_edges(self, tmp_python_repo: Path) -> None:
        """WHEN we scan and analyze the project"""
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        """THEN edges are detected between the modules"""
        assert graph.edge_count > 0
        targets = {e.target for e in graph.edges}
        assert "mylib/utils.py" in targets or "mylib/core.py" in targets

    """GIVEN a JavaScript project with imports"""
    def test_js_project_produces_edges(self, tmp_js_repo: Path) -> None:
        """WHEN we scan and analyze the project"""
        config = CodeMapConfig(repo_path=tmp_js_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        """THEN edges are detected"""
        assert graph.edge_count > 0

    """GIVEN a JS project with nested directories"""
    def test_groups_created_from_directories(self, tmp_js_repo: Path) -> None:
        """WHEN we scan and analyze the project"""
        config = CodeMapConfig(repo_path=tmp_js_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        """THEN groups are created for each directory level"""
        group_ids = set(graph.groups.keys())
        assert "src" in group_ids
        assert "src/components" in group_ids
        assert "src/utils" in group_ids

    """GIVEN an analyzed Python project"""
    def test_metrics_computed(self, tmp_python_repo: Path) -> None:
        """WHEN we check whether fan metrics are set"""
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)
        has_nonzero_metric = any(
            n.metrics.fan_in > 0 or n.metrics.fan_out > 0 for n in graph.nodes.values()
        )

        """THEN at least some nodes have non-zero metrics"""
        assert has_nonzero_metric

    """GIVEN an empty directory"""
    def test_empty_repo_produces_empty_graph(self, tmp_empty_repo: Path) -> None:
        """WHEN we scan and analyze the project"""
        config = CodeMapConfig(repo_path=tmp_empty_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        """THEN the graph is empty but valid"""
        assert graph.node_count == 0
        assert graph.edge_count == 0


class TestGroupHierarchy:
    """Tests for the hierarchical grouping of files by directory."""

    """GIVEN a JS project containing src/components/ and src/utils/"""
    def test_parent_child_groups(self, tmp_js_repo: Path) -> None:
        """WHEN we inspect the group hierarchy"""
        config = CodeMapConfig(repo_path=tmp_js_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)
        components_group = graph.groups.get("src/components")
        utils_group = graph.groups.get("src/utils")

        """THEN both groups are children of 'src'"""
        assert components_group is not None
        assert components_group.parent == "src"
        assert utils_group is not None
        assert utils_group.parent == "src"

    """GIVEN an analyzed JS project"""
    def test_nodes_assigned_to_correct_group(self, tmp_js_repo: Path) -> None:
        """WHEN we check node group assignments"""
        config = CodeMapConfig(repo_path=tmp_js_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)
        app_node = graph.get_node("src/components/App.jsx")
        index_node = graph.get_node("src/index.js")

        """THEN each node is in the correct group"""
        assert app_node is not None
        assert app_node.group == "src/components"
        assert index_node is not None
        assert index_node.group == "src"


class TestReportGeneration:
    """Tests for report generation from analyzed graphs."""

    """GIVEN an analyzed Python project"""
    def test_report_summary_counts(self, tmp_python_repo: Path) -> None:
        """WHEN we generate a report"""
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)
        report = generate_report(graph, config)

        """THEN summary counts match the graph"""
        assert report.total_files == graph.node_count
        assert report.total_edges == graph.edge_count
        assert "python" in report.languages

    """GIVEN an analyzed Python project with dependencies"""
    def test_report_has_depended_on(self, tmp_python_repo: Path) -> None:
        """WHEN we generate a report"""
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)
        report = generate_report(graph, config)

        """THEN most_depended_on only contains files with fan-in greater than zero"""
        if report.most_depended_on:
            for _file_path, fan_in in report.most_depended_on:
                assert fan_in > 0


class TestGitAbsence:
    """Tests that analysis degrades gracefully when git is unavailable."""

    """GIVEN a directory that is not a git repository"""
    def test_no_crash_without_git(self, tmp_python_repo: Path) -> None:
        """WHEN we scan and analyze with git enabled"""
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=True)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        """THEN the graph is still valid, just without ownership data"""
        assert graph.node_count > 0
        for node in graph.nodes.values():
            assert node.ownership.contributor_count == 0


class TestAnalyzerProgressCallbacks:
    """Tests that analyze accepts optional progress callbacks."""

    """GIVEN a Python project and a stage collector list"""
    def test_on_stage_callback_is_called(self, tmp_python_repo: Path) -> None:
        """WHEN we analyze with an on_stage callback"""
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        stages: list[str] = []
        analyze(scan_result, config, on_stage=stages.append)

        """THEN multiple stages are reported"""
        assert len(stages) >= 3
        assert any("node" in s.lower() or "group" in s.lower() for s in stages)
        assert any("dependenc" in s.lower() for s in stages)
        assert any("metric" in s.lower() for s in stages)

    """GIVEN a Python project"""
    def test_analyze_works_without_callbacks(self, tmp_python_repo: Path) -> None:
        """WHEN we analyze without callbacks (backward-compatible)"""
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        """THEN it still produces a valid graph"""
        assert graph.node_count > 0


class TestBatchGitAnalyzer:
    """Tests for GitAnalyzer batch prefetch."""

    """GIVEN a non-git directory"""
    def test_prefetch_returns_empty_without_git(self, tmp_python_repo: Path) -> None:
        """WHEN we prefetch"""
        from codemap.infrastructure.git import GitAnalyzer

        git = GitAnalyzer(tmp_python_repo)
        git.prefetch(["some/file.py"])

        """THEN caches are populated (empty but not None) and queries do not fail"""
        assert git.get_file_churn(tmp_python_repo / "some" / "file.py") == 0

    """GIVEN a non-git directory with prefetch already called"""
    def test_get_ownership_after_prefetch(self, tmp_python_repo: Path) -> None:
        """WHEN we request ownership for a file"""
        from codemap.infrastructure.git import GitAnalyzer

        git = GitAnalyzer(tmp_python_repo)
        git.prefetch(["mylib/core.py"])
        info = git.get_ownership(tmp_python_repo / "mylib" / "core.py")

        """THEN it returns empty ownership info without errors"""
        assert info.contributor_count == 0


class TestProgressModule:
    """Tests for the AnalysisProgress helper module."""

    """GIVEN an AnalysisProgress instance wired to an in-memory console"""
    def test_progress_stage_prints(self) -> None:
        """WHEN we call stage/done/warn"""
        from io import StringIO

        from rich.console import Console

        from codemap.cli.progress import AnalysisProgress

        buf = StringIO()
        progress = AnalysisProgress(Console(file=buf, force_terminal=True))
        progress.stage("Testing...")
        progress.done("All good")
        progress.warn("Watch out")

        """THEN the output contains all messages"""
        output = buf.getvalue()
        assert "Testing" in output
        assert "All good" in output
        assert "Watch out" in output
