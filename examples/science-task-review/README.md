# End-to-end scientific benchmark example

This directory contains a checked-in Harbor task bundle exported from the Task Studio
draft in `../science-task-authoring`. It exists so an independent reviewer can open a
complete task without first generating local output:

```bash
uv run harbor-marimo review-task \
  examples/science-task-review/bayesian-posterior-convergence --port 2722
```

The task is synthetic and intentionally small. Its oracle and verifier are executable
demonstration fixtures, not evidence that the scientific task is ready for a production
benchmark. A domain reviewer should still assess whether the inputs, model, thresholds,
and requested evidence support the claimed scientific conclusion.
