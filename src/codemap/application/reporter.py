"""Report generation use-case — produces human-readable summaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from codemap.application.config import CodeMapConfig
from codemap.domain.model import CodeGraph


@dataclass
class HotspotEntry:
    file_path: str
    fan_in: int
    fan_out: int
    churn: int
    centrality: float
    contributors: int


@dataclass
class OwnershipEntry:
    file_path: str
    primary_owner: str
    total_commits: int
    last_modified: str | None
    contributor_count: int


@dataclass
class CodeMapReport:
    """A structured report summarising the analysis."""

    total_files: int = 0
    total_edges: int = 0
    total_groups: int = 0
    languages: list[str] = field(default_factory=list)
    hotspots: list[HotspotEntry] = field(default_factory=list)
    ownership: list[OwnershipEntry] = field(default_factory=list)
    most_depended_on: list[tuple[str, int]] = field(default_factory=list)
    highest_fan_out: list[tuple[str, int]] = field(default_factory=list)


def generate_report(graph: CodeGraph, config: CodeMapConfig) -> CodeMapReport:
    """Build a CodeMapReport from an analysed CodeGraph."""
    report = CodeMapReport(
        total_files=graph.node_count,
        total_edges=graph.edge_count,
        total_groups=len(graph.groups),
        languages=sorted(
            {n.language.value for n in graph.nodes.values() if n.language.value != "unknown"}
        ),
    )

    nodes_sorted = sorted(graph.nodes.values(), key=lambda n: n.metrics.fan_in, reverse=True)

    # Top depended-on files (highest fan-in)
    report.most_depended_on = [
        (n.file_path, n.metrics.fan_in) for n in nodes_sorted[:10] if n.metrics.fan_in > 0
    ]

    # Highest fan-out
    by_fanout = sorted(graph.nodes.values(), key=lambda n: n.metrics.fan_out, reverse=True)
    report.highest_fan_out = [
        (n.file_path, n.metrics.fan_out) for n in by_fanout[:10] if n.metrics.fan_out > 0
    ]

    # Hotspots
    for n in graph.nodes.values():
        if n.metrics.is_hotspot(config.hotspot_churn_threshold, config.hotspot_fanin_threshold):
            report.hotspots.append(
                HotspotEntry(
                    file_path=n.file_path,
                    fan_in=n.metrics.fan_in,
                    fan_out=n.metrics.fan_out,
                    churn=n.metrics.churn,
                    centrality=n.metrics.centrality,
                    contributors=n.ownership.contributor_count,
                )
            )
    report.hotspots.sort(key=lambda h: h.churn, reverse=True)

    # Ownership
    report.ownership = _build_ownership(graph)

    return report


def _build_ownership(graph: CodeGraph) -> list[OwnershipEntry]:
    entries: list[OwnershipEntry] = []
    for n in graph.nodes.values():
        owner = n.ownership.primary_owner
        if owner is None:
            continue
        entries.append(
            OwnershipEntry(
                file_path=n.file_path,
                primary_owner=owner.name,
                total_commits=n.ownership.total_commits,
                last_modified=n.ownership.last_modified,
                contributor_count=n.ownership.contributor_count,
            )
        )
    entries.sort(key=lambda e: e.total_commits, reverse=True)
    return entries


def save_report_json(report: CodeMapReport, output_dir: Path) -> Path:
    """Persist the report as JSON."""
    import json

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "codemap_report.json"

    data = {
        "summary": {
            "total_files": report.total_files,
            "total_edges": report.total_edges,
            "total_groups": report.total_groups,
            "languages": report.languages,
        },
        "hotspots": [
            {
                "file": h.file_path,
                "fan_in": h.fan_in,
                "fan_out": h.fan_out,
                "churn": h.churn,
                "centrality": h.centrality,
                "contributors": h.contributors,
            }
            for h in report.hotspots
        ],
        "most_depended_on": [{"file": f, "fan_in": c} for f, c in report.most_depended_on],
        "highest_fan_out": [{"file": f, "fan_out": c} for f, c in report.highest_fan_out],
        "ownership": [
            {
                "file": o.file_path,
                "primary_owner": o.primary_owner,
                "total_commits": o.total_commits,
                "last_modified": o.last_modified,
                "contributors": o.contributor_count,
            }
            for o in report.ownership
        ],
    }

    path.write_text(json.dumps(data, indent=2))
    return path
