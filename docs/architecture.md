# Architecture

CodeMap is structured as a **layered application** with clean separation between concerns.

## Layer Diagram

```
┌──────────────────────────────┐
│          CLI Layer           │  Typer commands, argument parsing
│   codemap/cli/               │  Thin - delegates to Application
├───────────────────────────── ┤
│      Application Layer       │  Use-case orchestration
│   codemap/application/       │  scan, analyze, graph, report
├───────────────────────────── ┤
│        Domain Layer          │  Core graph model, metrics, protocols
│   codemap/domain/            │  Zero external dependencies
├────────────── ┬──────────────┤
│ Infrastructure│  Rendering   │  Git, filesystem,   │ JSON, HTML,
│ codemap/      │  codemap/    │  extractors         │ terminal
│ infrastructure│  rendering/  │                     │
└────────────── ┴──────────────┘
```

## Domain Layer (`codemap/domain/`)

The domain layer is the core - it has **no external dependencies** (only Python stdlib).

### Key types

| Type | Purpose |
|------|---------|
| `Node` | A file, directory, or module in the graph |
| `Edge` | A directed dependency between two nodes |
| `NodeGroup` | A logical cluster (directory, package) |
| `CodeGraph` | The central aggregate - nodes, edges, groups |
| `NodeMetrics` | Fan-in, fan-out, centrality, churn per node |
| `OwnershipInfo` | Contributor data attached to a node |
| `ContributorInfo` | Individual contributor snapshot |

### Protocols

| Protocol | Purpose |
|----------|---------|
| `DependencyExtractor` | Extracts edges from a source file |
| `OwnershipProvider` | Provides contributor data per file |
| `GraphRenderer` | Renders a CodeGraph to an output format |

All protocols use `typing.Protocol` with `runtime_checkable` for structural subtyping - implementors don't need to inherit from anything.

## Infrastructure Layer (`codemap/infrastructure/`)

Handles all external I/O and language-specific logic.

### FileScanner

Walks the repository tree with configurable include/exclude rules and ignored directory lists. Produces `ScanResult` containing `ScannedFile` entries.

### GitAnalyzer

Shells out to `git log` to extract per-file contributor and churn data. Implements `OwnershipProvider`. Degrades gracefully when git is unavailable.

**Batch mode (default):** Uses `prefetch()` to load ownership and churn for all files in two `git log` calls total, regardless of repository size. This replaces the previous 2×N per-file subprocess approach and is critical for performance on large repositories (e.g. Angular: ~6200 files).

### Extractors

Each extractor implements `DependencyExtractor`:

| Extractor | Strategy |
|-----------|----------|
| `PythonExtractor` | AST parsing of `import` / `from … import` statements |
| `JavaScriptExtractor` | Regex-based parsing of ES `import` and CommonJS `require` |

## Application Layer (`codemap/application/`)

Orchestrates domain and infrastructure into use-cases:

| Module | Use-case |
|--------|----------|
| `scanner.py` | Scan a repository → `ScanResult` |
| `analyzer.py` | Scan + extract deps + git + metrics → `CodeGraph` |
| `grapher.py` | Render a `CodeGraph` to HTML or JSON |
| `reporter.py` | Generate a `CodeMapReport` with hotspots and ownership |

## Rendering Layer (`codemap/rendering/`)

| Renderer | Output |
|----------|--------|
| `JsonRenderer` | Machine-readable `codemap.json` |
| `HtmlGraphRenderer` | Interactive D3.js visualization with multiple layouts, view modes, risk overlay, and exploration controls (`codemap.html`) |
| `PdfReportRenderer` | Multi-page PDF report with tables and metrics (`codemap.pdf`) |
| `terminal_renderer` | Rich console output for `codemap report` |

The HTML template is separated into `_html_template.py` for maintainability. The renderer pre-computes risk scores and topological depth in Python and passes enriched data to the D3.js client-side visualization.

### HTML Visualization Architecture

The HTML output is structured to be extensible:

- **Layout engines** are separate JS functions (`computeHierarchy`, `computeRadial`, `computeCluster`, `computeFlow`) - adding a new layout means adding one function and one toolbar button. The **Manual** layout mode stops the simulation and pins nodes via `fx`/`fy`; a `manualTick()` function updates the DOM during drag. Save/restore uses `localStorage` with per-page keys.
- **Color modes** are handled by a single `nodeColor(d)` function dispatching on `colorMode` state.
- **View modes** (All / Neighborhood / Impact) are applied via the `applyView()` function which sets node dimming state.
- **Display modes** (Overview / Readable / Focus / Presentation / Spacious) control label visibility and force spacing via `modeSpacing()` and `labelCollisionR()`.
- **Focused Node Exploration** is a first-class mode: `activateFocusedNode()` / `applyFocusedNodeView()` isolate a selected node's subgraph with sub-modes (local, deps, reverse, impact, flow).
- **Sidebar tabs** are independent panels - new tabs can be added without affecting existing ones.
- **Minimap** provides navigation for large, spacious graphs via `buildMinimap()`.
- **Node Notes** (`nodeNotes` Map) allow annotations on any node, with in-graph indicators and a modal editor (hidden by default, shown only on user action). Notes are stored in-memory per session.
- **Author accordion** (`buildAuthorsTab()`) renders expandable per-contributor panels with commit counts, file lists, risk metrics, and clickable file navigation. Selecting an author dims unrelated nodes on the graph.
- **I18N** uses a `T(key)` function backed by per-language dictionaries; all ~100 UI strings go through this function. Polish and English are fully supported.

## CLI Layer (`codemap/cli/`)

Thin Typer commands that parse arguments and delegate to the application layer. No business logic lives here.

### Progress Reporting (`cli/progress.py`)

The `AnalysisProgress` module provides Rich-based progress feedback for long-running operations:

- **Spinners** for indeterminate work (e.g. scanning, git analysis)
- **Stage labels** (`► Extracting dependencies…`) for each pipeline phase
- **Success/warning indicators** (`✓` / `!`) for completed stages
- **Progress bars** for countable work (available but optional)

All CLI commands wrap operations with `AnalysisProgress` and handle `Ctrl+C` gracefully with a clean `Cancelled.` message and exit code 130.

## Large-Graph Performance Architecture

The HTML visualization uses a **progressive rendering** strategy for large graphs (>200 nodes):

### Collapsed Cluster View

When `DATA.meta.nodeCount > 200`, the visualization automatically:

1. **Collapses groups** - Directory groups with >5 files become single cluster nodes
2. **Remaps edges** - Edges between collapsed nodes are merged into cluster-level edges
3. **Supports click-to-expand** - Clicking a cluster node expands its member files
4. **Rebuilds the simulation** - The `rebuildGraph()` function reinitializes D3 data joins, forces, and event handlers

### Adaptive Simulation Parameters

The `simParams()` function scales force simulation parameters based on node count:

| Node Count | Link Distance | Charge | Distance Max | Collision Iterations |
|------------|--------------|--------|-------------|----------------------|
| ≤200       | 280          | -800   | 1200        | 4                    |
| 200–500    | 320          | -1000  | 1600        | 3                    |
| >500       | 400          | -1200  | 2000        | 2                    |

### Throttled Tick

On large graphs, the simulation tick handler runs expensive DOM operations (hulls, hotspot rings, entry markers, note indicators) every 3rd tick instead of every tick, reducing CPU overhead.

### Performance Mode Toggle

The toolbar includes a **Fast / Quality** toggle (visible only for large graphs):
- **Fast** - collapsed clusters, stricter zoom-gated labels, throttled ticks
- **Quality** - all clusters expanded, full label visibility

### CLI `--fast` Flag

The `--fast` flag on `analyze` and `graph` commands skips git analysis (ownership, churn) entirely, reducing processing time for large repositories to structure-only analysis.

## Dependency Flow

```
CLI → Application → Domain
                  ↘ Infrastructure → Domain
                  ↘ Rendering → Domain
```

The domain layer is depended on by all other layers but depends on nothing. This ensures the core model can be tested in isolation and evolved independently.

## Extension Points

1. **New language analyzer** → implement `DependencyExtractor`, register in `analyzer.py`
2. **New output format** → implement `GraphRenderer`, register in `grapher.py`
3. **New ownership strategy** → implement `OwnershipProvider`
4. **New metrics** → extend `compute_all_metrics()` in `domain/metrics.py`
5. **CI validation rules** → consume `CodeGraph` or `CodeMapReport`
6. **New performance strategy** → extend `simParams()` in the HTML template or add analysis depth levels in `analyzer.py`

## Theme System

The HTML visualization supports three theme modes:

| Mode     | Behavior |
|----------|----------|
| **System** (default) | Follows the OS `prefers-color-scheme` media query |
| **Dark** | GitHub-inspired dark palette (`:root` variables) |
| **Light** | GitHub-inspired light palette (`[data-theme="light"]` override) |

Theme selection is persisted in `localStorage` (`codemap-theme` key). The `applyTheme()` function sets or removes the `data-theme` attribute on `<html>`. All UI elements use CSS custom properties (`--bg0`–`--bg3`, `--text`, `--accent`, etc.) ensuring consistent theming across sidebar, toolbar, graph, and overlays.
