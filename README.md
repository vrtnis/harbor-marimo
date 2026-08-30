# Marimo + Harbor

`harbor-marimo` turns [Harbor](https://harborframework.com/) jobs and
[ATIF](https://harborframework.com/docs/agents/trajectory-format) trajectories into
reactive, reproducible [Marimo](https://marimo.io/) analysis workspaces.

Use Harbor to run and monitor evaluations; use `harbor-marimo` for custom comparisons,
domain evidence, and reproducible investigation. The [**Acto**](src/acto) folder contains
example domain-expert workflows built on the integration.

`harbor-marimo` is in active development. It is currently an alpha source package and is
not yet published to PyPI or listed as an official Harbor community integration.

## What it does

- Loads complete or in-progress Harbor jobs from job, trial, result, or ATIF paths.
- Normalizes jobs, trials, step rewards, trajectories, tool calls, observations,
  artifacts, verifier files, and loader diagnostics into related tables.
- Preserves raw payloads and source provenance in the Python model and optional JSON export.
- Opens a generic Marimo workspace and provides an optional Harbor plugin for analysis
  handoff and table export.
- Includes scientific and financial Acto examples for task authoring, independent review,
  and evidence-linked result grading.

## Quick start from this repository

Python 3.12 or newer is required, matching Harbor 0.20.

```bash
uv sync --extra domain --extra plugin
uv run harbor-marimo examples/financial-review/demo_data/harbor_job
```

The first path implies `view`; use the explicit form for multiple jobs:

```bash
uv run harbor-marimo view jobs/eval-a jobs/eval-b --port 2718
```

Open the workspace in editable mode:

```bash
uv run harbor-marimo edit examples/financial-review/demo_data/harbor_job
```

Export normalized evidence for another analysis system:

```bash
uv run harbor-marimo export examples/financial-review/demo_data/harbor_job -o outputs/analysis.json
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

By default it prints a command for opening the completed job. It can also export normalized
JSON without starting a server:

```bash
uv run harbor run ... \
  --plugin marimo \
  --plugin-kwarg output_dir=outputs/harbor-marimo
```

The plugin is optional. Loading a saved Harbor job directly is the primary integration
contract.

Cloud execution remains a Harbor responsibility. See
[cloud sandbox compatibility](docs/cloud-sandboxes.md) for CoreWeave installation and
artifact handoff.

## Examples

- **Scientific:** An example Task Studio supports creating benchmark tasks, acceptance
  criteria, verifiers, and fixtures. The scientific applications also demonstrate
  independent task review, convergence signals, trial comparison, and persisted expert
  judgments. A pinned Terminal-Bench Science microarchitecture task adds an
  electrical-engineering example centered on ONNX model accuracy, ranking, and design
  selection.

  ```bash
  uv run acto studio examples/science-task-authoring/draft.json --port 2722
  uv run acto review-task \
    examples/science-task-review/bayesian-posterior-convergence
  ```

  See the [task-authoring](examples/science-task-authoring/README.md) and
  [scientific review](examples/science-review/README.md) examples, plus the
  [microarchitecture example](examples/microarchitecture-modeling/README.md) and
  [task-review lifecycle](docs/task-review.md).

- **Financial:** An example result-review application adds workbook-specific evidence and
  expert judgments to Harbor trials.

  ```bash
  uv run acto review-results examples/financial-review/demo_data/harbor_job \
    --domain financial --port 2718
  ```

  See the [financial review documentation](examples/financial-review/README.md).

See the [architecture](docs/architecture.md) and
[review-record documentation](docs/expert-reviews.md) for package responsibilities and
persistence details.

## Design

```text
Harbor job directories
        |
        v
tolerant read-only loader + path-safety checks
        |
        v
normalized evidence tables + retained raw payloads
        |
        +--> Python API / JSON export
        +--> generic Marimo analysis workspace
        +--> Acto example task and review applications
                         |
                         v
                external review sidecars
```

Artifacts are data, not trusted programs. A manifest destination that escapes its trial
step is marked unsafe and never resolved as evidence. Missing trajectories, manifests,
verifier output, or final job results become diagnostics instead of crashing the analysis.

## Development

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for scope and release expectations.
