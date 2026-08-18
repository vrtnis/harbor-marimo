# Acto financial-review example

This example shows the domain-expert layer that can be built on top of `harbor-marimo`.
It compares three synthetic Harbor trials for a financial forecast update, exposes their
ATIF evidence, and renders collected workbook artifacts with finance-specific review
semantics.

From the repository root:

```bash
uv sync --all-extras
uv run marimo run demo.py --port 2718
```

The app and fixtures currently live at the repository root for continuity with the proof
of concept:

- `demo.py` — Acto-specific Marimo application
- `demo_data/harbor_job/` — synthetic Harbor job with three trials
- `scripts/build_workbooks.mjs` — deterministic workbook fixture builder

The generic `harbor_marimo` package does not import this example or assume that an
artifact is a workbook. A future domain app can instead target code patches, browser
traces, research evidence, design assets, or another artifact contract.
