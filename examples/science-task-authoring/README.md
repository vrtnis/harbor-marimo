# Scientific task-authoring example

This example is a safe, synthetic Task Studio draft for a Bayesian convergence task.
It includes a known-good result, a deliberately non-converged result, and an illustrative
oracle path. The files demonstrate the authoring contract; the placeholder oracle must be
adapted to the final Harbor task environment before production use.

```bash
uv run acto studio examples/science-task-authoring/draft.json --port 2722
uv run acto test-verifier examples/science-task-authoring/draft.json
uv run acto export-task examples/science-task-authoring/draft.json \
  --output outputs/harbor-tasks/bayesian-posterior-convergence
uv run acto validate-task \
  outputs/harbor-tasks/bayesian-posterior-convergence --env docker
```

The last command prints the Harbor oracle and nop validation commands. Add `--run` only
when Docker or the selected Harbor sandbox provider is configured.
