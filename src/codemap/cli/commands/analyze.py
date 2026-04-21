"""``codemap analyze`` - build the code graph and show summary."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from codemap.application.analyzer import analyze as run_analyze
from codemap.application.config import CodeMapConfig
from codemap.application.scanner import scan_repository
from codemap.cli.progress import AnalysisProgress

console = Console()


def analyze(
    repo: Path = typer.Argument(Path("."), help="Path to the repository root."),
    no_git: bool = typer.Option(False, "--no-git", help="Disable git analysis."),
    fast: bool = typer.Option(False, "--fast", help="Fast mode - skip git analysis for speed."),
) -> None:
    """Analyze repository dependencies, ownership, and metrics."""
    config = CodeMapConfig(repo_path=repo.resolve(), enable_git=not no_git and not fast)
    progress = AnalysisProgress(console)

    try:
        with progress.spinner("Scanning repository…"):
            try:
                scan_result = scan_repository(config)
            except FileNotFoundError as exc:
                console.print(f"[red]Error:[/red] {exc}")
                raise typer.Exit(1) from exc

        console.print(f"\n[cyan]◆ CodeMap Analyze[/cyan]  {scan_result.root}")
        progress.done(f"Scanned {scan_result.file_count} files")

        graph = run_analyze(
            scan_result,
            config,
            on_stage=progress.stage,
        )

        progress.done(
            f"Nodes: {graph.node_count}  │  Edges: {graph.edge_count}  │  Groups: {len(graph.groups)}"
        )

        hotspots = [
            n
            for n in graph.nodes.values()
            if n.metrics.is_hotspot(config.hotspot_churn_threshold, config.hotspot_fanin_threshold)
        ]
        if hotspots:
            progress.warn(f"Hotspots: {len(hotspots)}")

        console.print()

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        raise typer.Exit(130) from None
