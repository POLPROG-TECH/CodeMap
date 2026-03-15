"""Rich-based progress reporting for long-running CodeMap operations."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from rich.status import Status


class AnalysisProgress:
    """Unified progress reporter for the multi-stage CodeMap analysis pipeline.

    Provides two modes:
    - **spinner** for indeterminate work (e.g. "Scanning repository…")
    - **bar** for countable work (e.g. "Extracting dependencies… 412/6195")

    All output goes through a single Rich console for clean rendering.
    """

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()
        self._progress: Progress | None = None
        self._status: Status | None = None
        self._task_id: TaskID | None = None

    @property
    def console(self) -> Console:
        return self._console

    # -- context managers --------------------------------------------------

    @contextmanager
    def spinner(self, message: str) -> Generator[None, None, None]:
        """Show a spinner with *message* while work is in progress."""
        with self._console.status(f"  {message}", spinner="dots") as st:
            self._status = st
            try:
                yield
            finally:
                self._status = None

    @contextmanager
    def bar(self, label: str, total: int) -> Generator[_BarHandle, None, None]:
        """Show a progress bar for *total* items."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("  {task.description}"),
            BarColumn(bar_width=30),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self._console,
            transient=True,
        )
        with progress:
            task = progress.add_task(label, total=total)
            handle = _BarHandle(progress, task)
            yield handle

    # -- convenience -------------------------------------------------------

    def stage(self, message: str) -> None:
        """Print a stage label like '  ► Extracting dependencies…'."""
        self._console.print(f"  [dim]►[/dim] {message}")

    def done(self, message: str) -> None:
        """Print a success line like '  ✓ Built 6195 nodes'."""
        self._console.print(f"  [green]✓[/green] {message}")

    def warn(self, message: str) -> None:
        """Print a warning line."""
        self._console.print(f"  [yellow]![/yellow] {message}")


class _BarHandle:
    """Thin wrapper returned by ``AnalysisProgress.bar``."""

    def __init__(self, progress: Progress, task: TaskID) -> None:
        self._progress = progress
        self._task = task

    def advance(self, n: int = 1) -> None:
        self._progress.advance(self._task, n)

    def update(self, **kwargs: Any) -> None:
        self._progress.update(self._task, **kwargs)
