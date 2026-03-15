"""Git-based ownership and churn analysis."""

from __future__ import annotations

import logging
import subprocess
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path

from codemap.domain.model import ContributorInfo, OwnershipInfo

logger = logging.getLogger(__name__)


class GitAnalyzer:
    """
    Extracts contributor and churn information from a git repository.

    Degrades gracefully when git is unavailable or the path has no history.
    Uses **batch** git log to avoid per-file subprocess overhead.
    """

    def __init__(self, repo_root: Path, max_commits: int = 1000) -> None:
        self._repo_root = repo_root.resolve()
        self._max_commits = max_commits
        self._available: bool | None = None
        # Batch caches (populated by prefetch)
        self._ownership_cache: dict[str, OwnershipInfo] | None = None
        self._churn_cache: dict[str, int] | None = None

    # -- OwnershipProvider contract ----------------------------------------

    def is_available(self) -> bool:
        if self._available is None:
            self._available = self._check_git()
        return self._available

    def prefetch(
        self,
        file_paths: list[str],
        on_progress: Callable[[int], None] | None = None,
    ) -> None:
        """Batch-load ownership and churn for all *file_paths* in two git calls.

        This replaces the previous 2×N subprocess approach with 2 total calls
        regardless of repository size.
        """
        if not self.is_available():
            self._ownership_cache = {}
            self._churn_cache = {}
            return

        self._ownership_cache = self._batch_ownership(file_paths, on_progress)
        self._churn_cache = self._batch_churn(file_paths)

    def get_ownership(self, file_path: Path) -> OwnershipInfo:
        rel = self._rel(file_path)
        if rel is None:
            return OwnershipInfo()
        if self._ownership_cache is not None:
            return self._ownership_cache.get(rel, OwnershipInfo())
        # Fallback to per-file if prefetch was not called
        return self._single_file_ownership(rel)

    def get_file_churn(self, file_path: Path) -> int:
        rel = self._rel(file_path)
        if rel is None:
            return 0
        if self._churn_cache is not None:
            return self._churn_cache.get(rel, 0)
        return self._single_file_churn(rel)

    # -- batch methods -----------------------------------------------------

    def _batch_ownership(
        self,
        file_paths: list[str],
        on_progress: Callable[[int], None] | None = None,
    ) -> dict[str, OwnershipInfo]:
        """Run a single ``git log`` with ``--name-only`` to collect per-file commits."""
        raw = self._run(
            [
                "git",
                "log",
                f"--max-count={self._max_commits}",
                "--format=__COMMIT__%aN|%aE|%aI",
                "--name-only",
            ],
            timeout=120,
        )
        if not raw:
            return {}

        file_set = set(file_paths)
        # per-file: list of (name, email, date) tuples in commit order
        file_commits: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
        current_author: tuple[str, str, str] | None = None
        processed = 0

        for line in raw.splitlines():
            if line.startswith("__COMMIT__"):
                parts = line[len("__COMMIT__") :].split("|", 2)
                if len(parts) >= 3:
                    current_author = (parts[0].strip(), parts[1].strip(), parts[2].strip())
            elif line.strip() and current_author:
                fname = line.strip()
                if fname in file_set:
                    file_commits[fname].append(current_author)
                    processed += 1
                    if on_progress and processed % 500 == 0:
                        on_progress(processed)

        result: dict[str, OwnershipInfo] = {}
        for rel, commits in file_commits.items():
            contributors: dict[str, ContributorInfo] = {}
            last_modifier: str | None = None
            last_date: str | None = None

            for i, (name, email, date) in enumerate(commits):
                if i == 0:
                    last_modifier = name
                    last_date = date
                key = email or name
                if key in contributors:
                    existing = contributors[key]
                    contributors[key] = ContributorInfo(
                        name=name,
                        email=email,
                        commit_count=existing.commit_count + 1,
                        last_commit_date=existing.last_commit_date,
                        first_commit_date=date,
                    )
                else:
                    contributors[key] = ContributorInfo(
                        name=name,
                        email=email,
                        commit_count=1,
                        last_commit_date=date,
                        first_commit_date=date,
                    )

            contributor_list = sorted(
                contributors.values(), key=lambda c: c.commit_count, reverse=True
            )
            result[rel] = OwnershipInfo(
                contributors=contributor_list,
                total_commits=sum(c.commit_count for c in contributor_list),
                last_modified=last_date,
                last_modifier=last_modifier,
            )

        return result

    def _batch_churn(self, file_paths: list[str]) -> dict[str, int]:
        """Count commits per file using a single ``git log --name-only``."""
        raw = self._run(
            [
                "git",
                "log",
                f"--max-count={self._max_commits}",
                "--format=__SEP__",
                "--name-only",
            ],
            timeout=120,
        )
        if not raw:
            return {}

        file_set = set(file_paths)
        churn: dict[str, int] = defaultdict(int)

        in_commit = False
        for line in raw.splitlines():
            if line.startswith("__SEP__"):
                in_commit = True
                continue
            fname = line.strip()
            if in_commit and fname and fname in file_set:
                churn[fname] += 1

        return dict(churn)

    # -- single-file fallbacks (used if prefetch not called) ---------------

    def _single_file_ownership(self, rel: str) -> OwnershipInfo:
        raw = self._run(
            [
                "git",
                "log",
                f"--max-count={self._max_commits}",
                "--format=%aN|%aE|%aI",
                "--",
                rel,
            ]
        )
        if not raw:
            return OwnershipInfo()

        contributors: dict[str, ContributorInfo] = {}
        last_modifier: str | None = None
        last_date: str | None = None

        for i, line in enumerate(raw.strip().splitlines()):
            parts = line.split("|", 2)
            if len(parts) < 3:
                continue
            name, email, date = parts[0].strip(), parts[1].strip(), parts[2].strip()

            if i == 0:
                last_modifier = name
                last_date = date

            key = email or name
            if key in contributors:
                existing = contributors[key]
                contributors[key] = ContributorInfo(
                    name=name,
                    email=email,
                    commit_count=existing.commit_count + 1,
                    last_commit_date=existing.last_commit_date,
                    first_commit_date=date,
                )
            else:
                contributors[key] = ContributorInfo(
                    name=name,
                    email=email,
                    commit_count=1,
                    last_commit_date=date,
                    first_commit_date=date,
                )

        contributor_list = sorted(contributors.values(), key=lambda c: c.commit_count, reverse=True)

        return OwnershipInfo(
            contributors=contributor_list,
            total_commits=sum(c.commit_count for c in contributor_list),
            last_modified=last_date,
            last_modifier=last_modifier,
        )

    def _single_file_churn(self, rel: str) -> int:
        raw = self._run(
            [
                "git",
                "log",
                f"--max-count={self._max_commits}",
                "--oneline",
                "--",
                rel,
            ]
        )
        if not raw:
            return 0
        return len(raw.strip().splitlines())

    # -- internals ---------------------------------------------------------

    def _check_git(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self._repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _run(self, cmd: list[str], timeout: int = 30) -> str | None:
        try:
            result = subprocess.run(
                cmd,
                cwd=self._repo_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                return None
            return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            logger.debug("Git command failed: %s", exc)
            return None

    def _rel(self, file_path: Path) -> str | None:
        try:
            return str(file_path.resolve().relative_to(self._repo_root))
        except ValueError:
            return None
