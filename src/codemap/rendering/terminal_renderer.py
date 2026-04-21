"""Rich-powered terminal summary renderer."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from codemap.application.reporter import CodeMapReport


def print_report(report: CodeMapReport, console: Console | None = None) -> None:
    """Pretty-print a CodeMapReport to the terminal."""
    con = console or Console()

    # Header
    header = Text()
    header.append("◆ CodeMap Report\n", style="bold cyan")
    header.append(f"  Files: {report.total_files}  │  ")
    header.append(f"Edges: {report.total_edges}  │  ")
    header.append(f"Groups: {report.total_groups}  │  ")
    header.append(f"Languages: {', '.join(report.languages) or '-'}")
    con.print(Panel(header, border_style="cyan"))

    # Hotspots
    if report.hotspots:
        table = Table(title="🔥 Hotspots", title_style="bold red", border_style="red")
        table.add_column("File", style="white", no_wrap=True)
        table.add_column("Churn", justify="right")
        table.add_column("Fan-in", justify="right")
        table.add_column("Fan-out", justify="right")
        table.add_column("Centrality", justify="right")
        table.add_column("Contributors", justify="right")
        for h in report.hotspots[:15]:
            table.add_row(
                h.file_path,
                str(h.churn),
                str(h.fan_in),
                str(h.fan_out),
                f"{h.centrality:.3f}",
                str(h.contributors),
            )
        con.print(table)

    # Most depended-on
    if report.most_depended_on:
        table = Table(
            title="📌 Most Depended-On Files", title_style="bold yellow", border_style="yellow"
        )
        table.add_column("File", style="white", no_wrap=True)
        table.add_column("Fan-in", justify="right")
        for f, c in report.most_depended_on:
            table.add_row(f, str(c))
        con.print(table)

    # Highest fan-out
    if report.highest_fan_out:
        table = Table(
            title="🔗 Highest Fan-Out Files", title_style="bold magenta", border_style="magenta"
        )
        table.add_column("File", style="white", no_wrap=True)
        table.add_column("Fan-out", justify="right")
        for f, c in report.highest_fan_out:
            table.add_row(f, str(c))
        con.print(table)

    # Ownership summary
    if report.ownership:
        table = Table(title="👤 Ownership Summary", title_style="bold green", border_style="green")
        table.add_column("File", style="white", no_wrap=True)
        table.add_column("Owner", style="cyan")
        table.add_column("Commits", justify="right")
        table.add_column("Contributors", justify="right")
        for o in report.ownership[:15]:
            table.add_row(
                o.file_path,
                o.primary_owner,
                str(o.total_commits),
                str(o.contributor_count),
            )
        con.print(table)
