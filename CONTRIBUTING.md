# Contributing

`harbor-marimo` is an analysis integration. Changes should preserve the boundary between
generic Harbor evidence and domain-specific interpretation.

## Development setup

```bash
uv sync --all-extras
uv run python -m unittest discover -s tests -v
uv run marimo check src/harbor_marimo/app.py examples/financial-review/app.py
uv build
```

## Compatibility rules

- Treat saved Harbor jobs as read-only.
- Keep reward dimensions named; do not infer universal pass/fail semantics.
- Preserve provenance through job, trial, and multi-step normalization.
- Parse all ATIF tool calls and observation results, including multimodal-safe summaries.
- Report absent or malformed optional evidence through diagnostics.
- Never execute or implicitly trust collected artifacts.
- Put domain renderers and domain decisions in examples or optional packages, not the core
  loader.

Before a public release, fixtures should be checked against the supported Harbor release
and the source distribution and wheel contents should be inspected.
