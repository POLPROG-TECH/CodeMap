# Changelog

All notable changes to CodeMap will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-15

### Added

- Initial release of CodeMap
- Framework-agnostic repository scanning for Python, JavaScript, TypeScript, JSX, TSX
- Module-level dependency extraction with fan-in/fan-out metrics
- Git-based ownership analysis with batch `git log` operations (2 calls regardless of repo size)
- Churn and hotspot detection (high churn × high coupling = risk)
- Interactive HTML visualization with D3.js force-directed graph
- Six layout modes: Force, Tree, Radial, Cluster, Flow, Manual
- Five display modes: Overview, Readable, Focus, Presentation, Spacious
- Five color modes: Language, Group, Churn, Risk, Contributors
- Theme selector: Dark, Light, System (persisted in localStorage)
- Complete Polish (PL) and English (EN) UI localization
- Focused single-node exploration with dropdown selection (Local, Dependencies, Reverse, Impact, Flow)
- Manual layout mode with drag-and-drop, save/restore via localStorage
- Node notes/annotations with modal editor
- Minimap for large-graph navigation
- Large-graph progressive loading: collapsed clusters, click-to-expand, adaptive simulation
- Fast/Quality performance toggle for large graphs (>200 nodes)
- `--fast` CLI flag to skip git analysis for speed
- Real-time progress reporting with Rich spinners and stage labels
- Graceful `Ctrl+C` cancellation for all commands
- JSON, HTML, and PDF output formats
- Terminal report renderer
- CI workflow with lint (ruff), format check, type checking (mypy), and tests
- 136 tests covering rendering, CLI, analysis, scanning, and infrastructure
- Comprehensive documentation: README, architecture, contributing guide
