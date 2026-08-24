# Contributing

`harbor-marimo` is the generic analysis integration. `acto` contains domain-specific task
authoring and review applications. Changes should keep those responsibilities clear.

## Development setup

```bash
uv sync --extra domain --extra plugin
uv run python -m unittest discover -s tests -v
uv run marimo check src/harbor_marimo/apps/analysis.py \
  src/acto/apps/expert_review.py \
  src/acto/apps/science_review.py \
  src/acto/apps/task_studio.py \
  src/acto/apps/task_review.py
uv build
```

## Compatibility rules

- Treat saved Harbor jobs as read-only.
- Keep reward dimensions named; do not infer universal pass/fail semantics.
- Preserve provenance through job, trial, and multi-step normalization.
- Parse all ATIF tool calls and observation results, including multimodal-safe summaries.
- Report absent or malformed optional evidence through diagnostics.
- Never execute or implicitly trust collected artifacts.
- Put domain renderers and domain decisions in `acto/domains/` and `acto/apps/`, not the
  core loader.
- Keep expert review sidecars outside canonical Harbor job directories.
- Keep cloud provider credentials and lifecycle code in Harbor, not `harbor-marimo`.

Before a public release, fixtures should be checked against the supported Harbor release
and the source distribution and wheel contents should be inspected.
