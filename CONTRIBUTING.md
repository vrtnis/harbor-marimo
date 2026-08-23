# Contributing

`harbor-marimo` is an analysis integration. Changes should preserve the boundary between
generic Harbor evidence and domain-specific interpretation.

## Development setup

```bash
uv sync --extra domain --extra plugin
uv run python -m unittest discover -s tests -v
uv run marimo check src/harbor_marimo/apps/analysis.py \
  src/harbor_marimo/apps/expert_review.py \
  src/harbor_marimo/apps/science_review.py
uv build
```

## Compatibility rules

- Treat saved Harbor jobs as read-only.
- Keep reward dimensions named; do not infer universal pass/fail semantics.
- Preserve provenance through job, trial, and multi-step normalization.
- Parse all ATIF tool calls and observation results, including multimodal-safe summaries.
- Report absent or malformed optional evidence through diagnostics.
- Never execute or implicitly trust collected artifacts.
- Put domain renderers and domain decisions in `domains/` and packaged apps, not the core
  loader.
- Keep expert review sidecars outside canonical Harbor job directories.
- Keep cloud provider credentials and lifecycle code in Harbor, not `harbor-marimo`.

Before a public release, fixtures should be checked against the supported Harbor release
and the source distribution and wheel contents should be inspected.
