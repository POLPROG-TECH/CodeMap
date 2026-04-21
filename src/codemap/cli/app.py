"""CodeMap CLI - entry point and top-level Typer application."""

from __future__ import annotations

import typer
from rich.console import Console

from codemap import __version__

app = typer.Typer(
    name="codemap",
    help="Framework-agnostic repository analysis and architecture mapping tool.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[cyan]CodeMap[/cyan] v{__version__}")
        raise typer.Exit()


@app.callback()
def _callback(
    version: bool | None = typer.Option(  # noqa: UP007
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """CodeMap - understand your codebase at a glance."""


# Register sub-commands
from codemap.cli.commands import analyze as _analyze_mod  # noqa: E402
from codemap.cli.commands import graph as _graph_mod  # noqa: E402
from codemap.cli.commands import report as _report_mod  # noqa: E402
from codemap.cli.commands import scan as _scan_mod  # noqa: E402

app.command(name="scan")(_scan_mod.scan)
app.command(name="analyze")(_analyze_mod.analyze)
app.command(name="graph")(_graph_mod.graph)
app.command(name="report")(_report_mod.report)


def main() -> None:
    """Entry point for the ``codemap`` console script."""
    app()


if __name__ == "__main__":
    main()
