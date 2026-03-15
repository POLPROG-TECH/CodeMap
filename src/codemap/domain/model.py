"""Core domain model for CodeMap — graph nodes, edges, groups, ownership, and metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    """Classification of graph nodes."""

    FILE = "file"
    DIRECTORY = "directory"
    MODULE = "module"
    PACKAGE = "package"


class EdgeType(Enum):
    """Classification of dependency edges."""

    IMPORTS = "imports"
    DEPENDS_ON = "depends_on"


class Language(Enum):
    """Detected programming language of a source file."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JSX = "jsx"
    TSX = "tsx"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    CSHARP = "csharp"
    CPP = "cpp"
    C = "c"
    HTML = "html"
    CSS = "css"
    SCSS = "scss"
    VUE = "vue"
    SVELTE = "svelte"
    DART = "dart"
    SCALA = "scala"
    SHELL = "shell"
    SQL = "sql"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TOML = "toml"
    UNKNOWN = "unknown"

    @classmethod
    def from_extension(cls, ext: str) -> Language:
        mapping: dict[str, Language] = {
            ".py": cls.PYTHON,
            ".js": cls.JAVASCRIPT,
            ".mjs": cls.JAVASCRIPT,
            ".cjs": cls.JAVASCRIPT,
            ".ts": cls.TYPESCRIPT,
            ".jsx": cls.JSX,
            ".tsx": cls.TSX,
            ".java": cls.JAVA,
            ".go": cls.GO,
            ".rs": cls.RUST,
            ".rb": cls.RUBY,
            ".php": cls.PHP,
            ".swift": cls.SWIFT,
            ".kt": cls.KOTLIN,
            ".kts": cls.KOTLIN,
            ".cs": cls.CSHARP,
            ".cpp": cls.CPP,
            ".cc": cls.CPP,
            ".cxx": cls.CPP,
            ".hpp": cls.CPP,
            ".c": cls.C,
            ".h": cls.C,
            ".html": cls.HTML,
            ".htm": cls.HTML,
            ".css": cls.CSS,
            ".scss": cls.SCSS,
            ".sass": cls.SCSS,
            ".vue": cls.VUE,
            ".svelte": cls.SVELTE,
            ".dart": cls.DART,
            ".scala": cls.SCALA,
            ".sh": cls.SHELL,
            ".bash": cls.SHELL,
            ".zsh": cls.SHELL,
            ".sql": cls.SQL,
            ".json": cls.JSON,
            ".yaml": cls.YAML,
            ".yml": cls.YAML,
            ".md": cls.MARKDOWN,
            ".toml": cls.TOML,
        }
        return mapping.get(ext, cls.UNKNOWN)


# ---------------------------------------------------------------------------
# Ownership / contributor metadata
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContributorInfo:
    """Snapshot of a single contributor's involvement with a file or module."""

    name: str
    email: str
    commit_count: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    last_commit_date: str | None = None
    first_commit_date: str | None = None


@dataclass
class OwnershipInfo:
    """Aggregated ownership data for a node."""

    contributors: list[ContributorInfo] = field(default_factory=list)
    total_commits: int = 0
    last_modified: str | None = None
    last_modifier: str | None = None

    @property
    def primary_owner(self) -> ContributorInfo | None:
        if not self.contributors:
            return None
        return max(self.contributors, key=lambda c: c.commit_count)

    @property
    def contributor_count(self) -> int:
        return len(self.contributors)


# ---------------------------------------------------------------------------
# Node-level metrics
# ---------------------------------------------------------------------------


@dataclass
class NodeMetrics:
    """Computed metrics for a single graph node."""

    fan_in: int = 0
    fan_out: int = 0
    centrality: float = 0.0
    churn: int = 0

    def is_hotspot(self, churn_threshold: int = 10, fanin_threshold: int = 3) -> bool:
        return self.churn >= churn_threshold and self.fan_in >= fanin_threshold


# ---------------------------------------------------------------------------
# Graph primitives
# ---------------------------------------------------------------------------


@dataclass
class Node:
    """A single entity in the code graph (file, directory, module)."""

    id: str
    label: str
    node_type: NodeType
    file_path: str
    group: str = ""
    language: Language = Language.UNKNOWN
    line_count: int = 0
    ownership: OwnershipInfo = field(default_factory=OwnershipInfo)
    metrics: NodeMetrics = field(default_factory=NodeMetrics)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    """A directed dependency between two nodes."""

    source: str
    target: str
    edge_type: EdgeType = EdgeType.IMPORTS
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeGroup:
    """A logical grouping of nodes (directory, package, module cluster)."""

    id: str
    label: str
    parent: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Code graph — the central domain aggregate
# ---------------------------------------------------------------------------


@dataclass
class CodeGraph:
    """
    The central domain model: a directed graph of code entities, their
    dependency edges, logical groupings, and attached metadata.
    """

    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    groups: dict[str, NodeGroup] = field(default_factory=dict)
    root_path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    # -- mutators ----------------------------------------------------------

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        if edge.source in self.nodes and edge.target in self.nodes:
            self.edges.append(edge)

    def add_group(self, group: NodeGroup) -> None:
        self.groups[group.id] = group

    # -- queries -----------------------------------------------------------

    def get_dependencies(self, node_id: str) -> list[Edge]:
        """Edges *from* this node (what it depends on)."""
        return [e for e in self.edges if e.source == node_id]

    def get_reverse_dependencies(self, node_id: str) -> list[Edge]:
        """Edges *into* this node (what depends on it)."""
        return [e for e in self.edges if e.target == node_id]

    def get_nodes_in_group(self, group_id: str) -> list[Node]:
        return [n for n in self.nodes.values() if n.group == group_id]

    def get_node(self, node_id: str) -> Node | None:
        return self.nodes.get(node_id)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)
