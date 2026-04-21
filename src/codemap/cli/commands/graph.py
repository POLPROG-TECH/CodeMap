"""``codemap graph`` - render an interactive HTML, JSON, or PDF graph."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from codemap.application.analyzer import analyze as run_analyze
from codemap.application.config import CodeMapConfig
from codemap.application.grapher import SUPPORTED_FORMATS, render_graph
from codemap.application.scanner import scan_repository
from codemap.cli.progress import AnalysisProgress

console = Console()


def graph(
    repo: Path = typer.Argument(Path("."), help="Path to the repository root."),
    output: Path = typer.Option(Path("codemap_output"), "--output", "-o", help="Output directory."),
    fmt: str = typer.Option("html", "--format", "-f", help="Output format: html, json, or pdf."),
    no_git: bool = typer.Option(False, "--no-git", help="Disable git analysis."),
    fast: bool = typer.Option(False, "--fast", help="Fast mode - skip git analysis for speed."),
) -> None:
    """Generate a visual dependency graph of the repository."""
    if fmt not in SUPPORTED_FORMATS:
        console.print(
            f"[red]Error:[/red] Unknown format '{fmt}'. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )
        raise typer.Exit(1)

    config = CodeMapConfig(
        repo_path=repo.resolve(),
        enable_git=not no_git and not fast,
        output_dir=output,
    )
    progress = AnalysisProgress(console)

    try:
        with progress.spinner("Scanning repository…"):
            try:
                scan_result = scan_repository(config)
            except FileNotFoundError as exc:
                console.print(f"[red]Error:[/red] {exc}")
                raise typer.Exit(1) from exc

        console.print(f"\n[cyan]◆ CodeMap Graph[/cyan]  {scan_result.root}")
        progress.done(f"Scanned {scan_result.file_count} files")

        code_graph = run_analyze(
            scan_result,
            config,
            on_stage=progress.stage,
        )

        progress.stage(f"Rendering {fmt.upper()} output…")
        try:
            out_path = render_graph(code_graph, config, fmt=fmt)
        except RuntimeError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1) from exc

        progress.done(f"Output written to: {out_path}")
        console.print()

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        raise typer.Exit(130) from None
