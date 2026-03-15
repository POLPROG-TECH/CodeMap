"""Tests for the full analysis pipeline and grouping/hierarchy logic."""

from __future__ import annotations

from pathlib import Path

from codemap.application.analyzer import analyze
from codemap.application.config import CodeMapConfig
from codemap.application.reporter import generate_report
from codemap.application.scanner import scan_repository


class TestAnalysisPipeline:
    """End-to-end analysis pipeline integration tests."""

    def test_python_project_produces_edges(self, tmp_python_repo: Path) -> None:
        # GIVEN a Python project with inter-module imports
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)

        # WHEN we scan and analyze
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # THEN edges are detected between the modules
        assert graph.edge_count > 0
        targets = {e.target for e in graph.edges}
        assert "mylib/utils.py" in targets or "mylib/core.py" in targets

    def test_js_project_produces_edges(self, tmp_js_repo: Path) -> None:
        # GIVEN a JavaScript project with imports
        config = CodeMapConfig(repo_path=tmp_js_repo, enable_git=False)

        # WHEN we scan and analyze
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # THEN edges are detected
        assert graph.edge_count > 0

    def test_groups_created_from_directories(self, tmp_js_repo: Path) -> None:
        # GIVEN a JS project with nested directories
        config = CodeMapConfig(repo_path=tmp_js_repo, enable_git=False)

        # WHEN we scan and analyze
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # THEN groups are created for each directory level
        group_ids = set(graph.groups.keys())
        assert "src" in group_ids
        assert "src/components" in group_ids
        assert "src/utils" in group_ids

    def test_metrics_computed(self, tmp_python_repo: Path) -> None:
        # GIVEN an analyzed Python project
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # WHEN we check if fan metrics are set
        has_nonzero_metric = any(
            n.metrics.fan_in > 0 or n.metrics.fan_out > 0 for n in graph.nodes.values()
        )

        # THEN at least some nodes have non-zero metrics
        assert has_nonzero_metric

    def test_empty_repo_produces_empty_graph(self, tmp_empty_repo: Path) -> None:
        # GIVEN an empty directory
        config = CodeMapConfig(repo_path=tmp_empty_repo, enable_git=False)

        # WHEN we scan and analyze
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # THEN the graph is empty but valid
        assert graph.node_count == 0
        assert graph.edge_count == 0


class TestGroupHierarchy:
    """Hierarchical grouping of files by directory."""

    def test_parent_child_groups(self, tmp_js_repo: Path) -> None:
        # GIVEN a JS project: src/components/, src/utils/
        config = CodeMapConfig(repo_path=tmp_js_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # WHEN we inspect group hierarchy
        components_group = graph.groups.get("src/components")
        utils_group = graph.groups.get("src/utils")

        # THEN both are children of "src"
        assert components_group is not None
        assert components_group.parent == "src"
        assert utils_group is not None
        assert utils_group.parent == "src"

    def test_nodes_assigned_to_correct_group(self, tmp_js_repo: Path) -> None:
        # GIVEN an analyzed JS project
        config = CodeMapConfig(repo_path=tmp_js_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # WHEN we check node group assignments
        app_node = graph.get_node("src/components/App.jsx")
        index_node = graph.get_node("src/index.js")

        # THEN each node is in the correct group
        assert app_node is not None
        assert app_node.group == "src/components"
        assert index_node is not None
        assert index_node.group == "src"


class TestReportGeneration:
    """Report generation from analyzed graphs."""

    def test_report_summary_counts(self, tmp_python_repo: Path) -> None:
        # GIVEN an analyzed Python project
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # WHEN we generate a report
        report = generate_report(graph, config)

        # THEN summary counts are correct
        assert report.total_files == graph.node_count
        assert report.total_edges == graph.edge_count
        assert "python" in report.languages

    def test_report_has_depended_on(self, tmp_python_repo: Path) -> None:
        # GIVEN an analyzed Python project with dependencies
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # WHEN we generate a report
        report = generate_report(graph, config)

        # THEN most_depended_on contains files with fan-in > 0
        if report.most_depended_on:
            for _file_path, fan_in in report.most_depended_on:
                assert fan_in > 0


class TestGitAbsence:
    """Analysis degrades gracefully when git is unavailable."""

    def test_no_crash_without_git(self, tmp_python_repo: Path) -> None:
        # GIVEN a directory that is NOT a git repo
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=True)

        # WHEN we scan and analyze (git will fail gracefully)
        scan_result = scan_repository(config)
        graph = analyze(scan_result, config)

        # THEN the graph is still valid, just without ownership data
        assert graph.node_count > 0
        for node in graph.nodes.values():
            assert node.ownership.contributor_count == 0


class TestAnalyzerProgressCallbacks:
    """The analyze function accepts optional progress callbacks."""

    def test_on_stage_callback_is_called(self, tmp_python_repo: Path) -> None:
        # GIVEN a Python project and a stage collector
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)
        stages: list[str] = []

        # WHEN we analyze with an on_stage callback
        analyze(scan_result, config, on_stage=stages.append)

        # THEN multiple stages are reported
        assert len(stages) >= 3
        assert any("node" in s.lower() or "group" in s.lower() for s in stages)
        assert any("dependenc" in s.lower() for s in stages)
        assert any("metric" in s.lower() for s in stages)

    def test_analyze_works_without_callbacks(self, tmp_python_repo: Path) -> None:
        # GIVEN a Python project
        config = CodeMapConfig(repo_path=tmp_python_repo, enable_git=False)
        scan_result = scan_repository(config)

        # WHEN we analyze without callbacks (backward-compatible)
        graph = analyze(scan_result, config)

        # THEN it still produces a valid graph
        assert graph.node_count > 0


class TestBatchGitAnalyzer:
    """GitAnalyzer batch prefetch."""

    def test_prefetch_returns_empty_without_git(self, tmp_python_repo: Path) -> None:
        # GIVEN a non-git directory
        from codemap.infrastructure.git import GitAnalyzer

        git = GitAnalyzer(tmp_python_repo)

        # WHEN we prefetch
        git.prefetch(["some/file.py"])

        # THEN caches are populated (empty but not None)
        assert git.get_file_churn(tmp_python_repo / "some" / "file.py") == 0

    def test_get_ownership_after_prefetch(self, tmp_python_repo: Path) -> None:
        # GIVEN a non-git directory with prefetch called
        from codemap.infrastructure.git import GitAnalyzer

        git = GitAnalyzer(tmp_python_repo)
        git.prefetch(["mylib/core.py"])

        # WHEN we get ownership
        info = git.get_ownership(tmp_python_repo / "mylib" / "core.py")

        # THEN it returns empty info (no git) without error
        assert info.contributor_count == 0


class TestProgressModule:
    """The AnalysisProgress helper module."""

    def test_progress_stage_prints(self) -> None:
        # GIVEN an AnalysisProgress instance
        from io import StringIO

        from rich.console import Console

        from codemap.cli.progress import AnalysisProgress

        buf = StringIO()
        progress = AnalysisProgress(Console(file=buf, force_terminal=True))

        # WHEN we call stage/done/warn
        progress.stage("Testing…")
        progress.done("All good")
        progress.warn("Watch out")

        # THEN output contains the messages
        output = buf.getvalue()
        assert "Testing" in output
        assert "All good" in output
        assert "Watch out" in output
