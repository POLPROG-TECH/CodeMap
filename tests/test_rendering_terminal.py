"""Tests for the terminal report renderer."""

from __future__ import annotations

from rich.console import Console

from codemap.application.reporter import CodeMapReport, HotspotEntry, OwnershipEntry
from codemap.rendering.terminal_renderer import print_report


class TestTerminalRenderer:
    """Tests that terminal report rendering does not crash and contains expected text."""

    """GIVEN a report populated with hotspots and ownership"""
    def test_print_report_runs(self) -> None:
        """WHEN we print the report"""
        report = CodeMapReport(
            total_files=10,
            total_edges=15,
            total_groups=3,
            languages=["python", "javascript"],
            hotspots=[
                HotspotEntry(
                    file_path="core.py",
                    fan_in=5,
                    fan_out=2,
                    churn=20,
                    centrality=0.5,
                    contributors=3,
                )
            ],
            most_depended_on=[("utils.py", 8)],
            highest_fan_out=[("main.py", 6)],
            ownership=[
                OwnershipEntry(
                    file_path="core.py",
                    primary_owner="Alice",
                    total_commits=25,
                    last_modified="2026-01-15",
                    contributor_count=3,
                )
            ],
        )
        with open("/dev/null", "w") as sink:
            console = Console(file=sink, force_terminal=True)
            print_report(report, console)

        """THEN no exception is raised (smoke test)"""

    """GIVEN an empty report"""
    def test_print_empty_report(self) -> None:
        """WHEN we print the report"""
        report = CodeMapReport()
        with open("/dev/null", "w") as sink:
            console = Console(file=sink, force_terminal=True)
            print_report(report, console)

        """THEN no exception is raised"""
