"""``codemap scan`` — discover repository files and technologies."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from codemap.application.config import CodeMapConfig
from codemap.application.scanner import scan_repository

console = Console()


def scan(
    repo: Path = typer.Argument(Path("."), help="Path to the repository root."),
    include: str | None = typer.Option(
        None, "--include", "-i", help="Comma-separated include glob patterns."
    ),  # noqa: UP007
    exclude: str | None = typer.Option(
        None, "--exclude", "-e", help="Comma-separated exclude glob patterns."
    ),  # noqa: UP007
) -> None:
    """Scan a repository and show discovered source files."""
    config = CodeMapConfig(
        repo_path=repo.resolve(),
        include_patterns=include.split(",") if include else [],
        exclude_patterns=exclude.split(",") if exclude else [],
    )

    try:
        result = scan_repository(config)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"\n[cyan]◆ CodeMap Scan[/cyan]  {result.root}\n")

    table = Table(border_style="dim")
    table.add_column("File", style="white", no_wrap=True)
    table.add_column("Language", style="cyan")
    table.add_column("Lines", justify="right")
    for f in sorted(result.files, key=lambda x: x.relative_path):
        table.add_row(f.relative_path, f.language.value, str(f.line_count))

    console.print(table)
    console.print(
        f"\n  [green]{result.file_count}[/green] files  │  "
        f"Languages: {', '.join(sorted(lang.value for lang in result.languages_detected)) or '—'}\n"
    )
