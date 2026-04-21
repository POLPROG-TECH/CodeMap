"""``codemap report`` - generate terminal and JSON reports."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from codemap.application.analyzer import analyze as run_analyze
from codemap.application.config import CodeMapConfig
from codemap.application.reporter import generate_report, save_report_json
from codemap.application.scanner import scan_repository
from codemap.cli.progress import AnalysisProgress
from codemap.rendering.terminal_renderer import print_report

console = Console()


def report(
    repo: Path = typer.Argument(Path("."), help="Path to the repository root."),
    output: Path = typer.Option(
        Path("codemap_output"), "--output", "-o", help="Output directory for JSON report."
    ),
    json_out: bool = typer.Option(False, "--json", help="Also save report as JSON."),
    no_git: bool = typer.Option(False, "--no-git", help="Disable git analysis."),
) -> None:
    """Generate a human-readable report with hotspots, ownership, and dependency insights."""
    config = CodeMapConfig(
        repo_path=repo.resolve(),
        enable_git=not no_git,
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

        console.print(f"\n[cyan]◆ CodeMap Report[/cyan]  {scan_result.root}")
        progress.done(f"Scanned {scan_result.file_count} files")

        code_graph = run_analyze(
            scan_result,
            config,
            on_stage=progress.stage,
        )

        progress.stage("Generating report…")
        rpt = generate_report(code_graph, config)

        print_report(rpt, console)

        if json_out:
            json_path = save_report_json(rpt, config.output_dir)
            progress.done(f"JSON report saved to: {json_path}")

        console.print()

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        raise typer.Exit(130) from None
