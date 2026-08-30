# Microarchitecture modeling example

This example combines an unchanged Terminal-Bench Science task with an adjacent Acto
review profile and a Marimo presentation layer for CPU design-space-exploration evidence.

- [`microarch-modeling/`](microarch-modeling/) is the pinned, standard Harbor task.
- [`microarch-modeling.review-profile.json`](microarch-modeling.review-profile.json)
  supplies expert-facing criteria, labels, and definitions without changing task execution.
- [`src/acto/domains/microarchitecture/`](../../src/acto/domains/microarchitecture/)
  presents stored ONNX identity and verifier metrics without loading or executing the model.

Review the benchmark task itself:

```bash
uv run acto review-task \
  examples/microarchitecture-modeling/microarch-modeling \
  --review-dir outputs/microarchitecture-task-reviews \
  --port 2722
```

After Harbor has run the task, review an agent result with the same criteria:

```bash
uv run acto review-results <harbor-job-directory> \
  --domain microarchitecture \
  --task examples/microarchitecture-modeling/microarch-modeling \
  --review-dir outputs/microarchitecture-result-reviews \
  --port 2723
```

Harbor still owns container or cloud-sandbox execution and scoring. Acto reads the saved
task and run evidence, while Marimo provides the reactive expert interface. See
[`UPSTREAM.md`](UPSTREAM.md) for the exact source and license provenance.

For interface development and screenshots, a clearly labeled reference fixture can be
opened without running the eight-hour benchmark:

```bash
uv run acto review-results \
  examples/microarchitecture-modeling/demo_data/harbor_job \
  --domain microarchitecture \
  --profile examples/microarchitecture-modeling/microarch-modeling.review-profile.json \
  --port 2723
```

The fixture uses the upstream reference solution artifact and metrics published in the
pinned task README. It is not an Acto production run or a substitute for Harbor validation.
