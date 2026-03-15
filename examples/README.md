# CodeMap Examples

This directory contains small but realistic example projects for demonstrating
CodeMap's analysis capabilities.

## Python Project (`python_project/`)

A small Python application with services, models, and utilities that import
each other — showing dependency extraction, grouping, and metrics.

```bash
codemap scan   examples/python_project
codemap graph  examples/python_project -o codemap_output/python_demo
codemap report examples/python_project
```

## JavaScript Project (`js_project/`)

A React-style JavaScript application with components, services, and utilities
demonstrating ES module import analysis.

```bash
codemap scan   examples/js_project
codemap graph  examples/js_project -o codemap_output/js_demo
codemap report examples/js_project
```
