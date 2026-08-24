# Harbor-Marimo with Acto expert workflows

`harbor-marimo` turns [Harbor](https://harborframework.com/) jobs and
[ATIF](https://harborframework.com/docs/agents/trajectory-format) trajectories into
reactive, reproducible [Marimo](https://marimo.io/) analysis workspaces.

The repository also packages `acto`, the domain-expert application layer for task
authoring, independent task review, and agent-result grading. Marimo supplies the reactive
application runtime; Harbor supplies the external task runner and canonical evidence
formats; Acto supplies the expert workflows and domain interpretation.

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
- Provides Acto financial and scientific result-review applications with durable,
  evidence-linked sidecars.
- Provides Acto Task Studio, which exports Terminal-Bench Science drafts as standard Harbor
  tasks with declarative, fixture-tested verifiers.
- Provides Acto Task Review for independent benchmark-item approval.

## Quick start from this repository

Python 3.12 or newer is required, matching Harbor 0.20.

```bash
uv sync --extra domain --extra plugin
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
uv run acto review-results examples/financial-review/demo_data/harbor_job \
  --domain financial \
  --review-dir outputs/reviews
```

Author a scientific benchmark task from the included synthetic draft:

```bash
uv run acto studio examples/science-task-authoring/draft.json --port 2722
```

See the [domain-expert task-authoring workflow](docs/task-authoring.md) for verifier
fixtures, Harbor export, oracle/nop validation, and CoreWeave handoff responsibilities.

Independently review the exported benchmark task itself:

```bash
uv run acto review-task \
  examples/science-task-review/bayesian-posterior-convergence \
  --review-dir outputs/task-reviews
```

The [task-review lifecycle](docs/task-review.md) separates author validation, domain review,
technical review, final benchmark approval, and later agent-result grading.

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

Cloud execution remains a Harbor concern. See [cloud sandbox compatibility](docs/cloud-sandboxes.md)
for the opt-in CoreWeave installation and the downstream artifact handoff.

## Domain example

A financial-review proof of concept remains available as a domain application:

```bash
uv run marimo run src/acto/apps/expert_review.py --port 2718
```

It adds workbook-specific review semantics on top of Harbor trials. See the
[domain example documentation](examples/financial-review/README.md).

The [scientific review example](examples/science-review/README.md) demonstrates bounded
artifact previews, convergence signals, trial comparison, and persisted expert judgments.
See the [architecture](docs/architecture.md), [Acto package](docs/acto-package.md), and
[review record](docs/expert-reviews.md) documentation for package responsibilities and the
persistence contract.

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
        +--> Acto task and review applications
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
