# Marimo + Harbor

`harbor-marimo` turns [Harbor](https://harborframework.com/) jobs and
[ATIF](https://harborframework.com/docs/agents/trajectory-format) trajectories into
reactive, reproducible [Marimo](https://marimo.io/) analysis workspaces.

It is the programmable analysis layer beside Harbor's operational viewer: use Harbor to
run and monitor evaluations; use `harbor-marimo` when an investigation needs custom
comparisons, domain evidence, or a notebook that can be reviewed and rerun.

`harbor-marimo` is in active development. It is currently an alpha source package and is
not yet published to PyPI or listed as an official Harbor community integration.

## What it does

- Loads one or more complete or in-progress Harbor job directories.
- Resolves job, trial, `result.json`, and ATIF paths to their enclosing jobs.
- Normalizes jobs, trials, step rewards, trajectories, tool calls, observations,
  artifacts, verifier files, and loader diagnostics into related tables.
- Preserves raw Harbor and ATIF payloads in the Python model and optional JSON export.
- Opens a generic Marimo workspace for comparisons and evidence inspection.
- Provides a small Harbor plugin that prints the analysis handoff and can export tables
  after a job.
- Keeps domain-specific applications separate. The included app is the first domain
  example.

## Quick start from this repository

Python 3.12 or newer is required, matching Harbor 0.20.

```bash
uv sync --all-extras
uv run harbor-marimo examples/financial-review/demo_data/harbor_job
```

The first positional path implies the `view` command. The explicit form supports more
than one job:

```bash
uv run harbor-marimo view jobs/eval-a jobs/eval-b --port 2718
```

Open the generic notebook in editable Marimo mode:

```bash
uv run harbor-marimo edit examples/financial-review/demo_data/harbor_job
```

Export normalized evidence for another analysis system:

```bash
uv run harbor-marimo export examples/financial-review/demo_data/harbor_job -o outputs/analysis.json
```

Open the expert workflow and persist judgments as sidecars:

```bash
uv run harbor-marimo review examples/financial-review/demo_data/harbor_job \
  --domain financial \
  --review-dir outputs/reviews
```

Add `--include-raw` only when the downstream consumer needs complete original payloads.
Exports retain source provenance and can contain absolute local paths. Keep local exports
under the ignored `outputs/` directory unless they have been reviewed and sanitized for
publication.

## Python API

```python
from harbor_marimo import load

bundle = load(["jobs/eval-a", "jobs/eval-b"])
tables = bundle.tables()

trials = tables["trials"]
tool_calls = tables["tool_calls"]
diagnostics = tables["diagnostics"]
```

The public normalized tables are:

| Table | Purpose |
| --- | --- |
| `jobs` | Job identity, state, tokens, and cost |
| `trials` | Task, agent, model, status, and unambiguous headline reward |
| `trial_steps` | Single-step and multi-step trial structure |
| `rewards` | Long-form named reward dimensions at trial or step scope |
| `trajectory_steps` | Every ATIF step, including known nested subagent trajectories |
| `tool_calls` | Every tool call and its arguments |
| `observations` | Every observation result and source call |
| `artifacts` | Manifest entries plus unlisted discovered files |
| `verifier_files` | Verifier file metadata and bounded safe-text previews |
| `diagnostics` | Missing, malformed, incomplete, or unsafe source findings |

Every evidence row carries job, trial, and step provenance where applicable.

## Optional Harbor plugin

The package registers the Harbor entry point `marimo`, in the same lightweight packaging
style as `harbor-atif2otel`:

```bash
uv run harbor run ... --plugin marimo
```

By default it prints a command for opening the completed job. To also create normalized
JSON without launching a server:

```bash
uv run harbor run ... \
  --plugin marimo \
  --plugin-kwarg output_dir=outputs/harbor-marimo
```

The plugin is optional. Loading a saved Harbor job directly is the primary integration
contract.

## Domain example

A financial-review proof of concept remains available as a domain application:

```bash
uv run marimo run src/harbor_marimo/apps/expert_review.py --port 2718
```

It adds workbook-specific review semantics on top of Harbor trials. See the
[domain example documentation](examples/financial-review/README.md).

## Design

```text
Harbor job directories
        |
        v
tolerant read-only loader + path boundary
        |
        v
normalized evidence tables + retained raw payloads
        |
        +--> Python API / JSON export
        +--> generic Marimo analysis workspace
        +--> domain-specific Marimo applications
```

Artifacts are data, not trusted programs. A manifest destination that escapes its trial
step is marked unsafe and never resolved as evidence. Missing trajectories, manifests,
verifier output, or final job results become diagnostics instead of crashing the analysis.

## Development

```bash
uv sync --all-extras
uv run python -m unittest discover -s tests -v
uv run marimo check src/harbor_marimo/apps/analysis.py src/harbor_marimo/apps/expert_review.py
uv build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for scope and release expectations.
