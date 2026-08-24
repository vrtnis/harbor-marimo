# Domain-expert task authoring

Task Studio lets a scientist express a Terminal-Bench Science task without editing Python,
TOML, shell tests, or container configuration. It produces a standard Harbor task bundle;
it does not replace Harbor's task runner or sandbox providers.

## Expert workflow

1. Define the scientific question, task instruction, authorship, and conflicts.
2. Specify the result files and structured fields that make the answer auditable.
3. Map scientific acceptance criteria to declarative checks. Criteria that require judgment
   can be marked expert-only.
4. supply a known-good and known-bad result and test that the verifier distinguishes them.
5. save a versioned draft, export the Harbor task, and run oracle/nop validation.

Start with the included synthetic example:

```bash
uv run harbor-marimo author examples/science-task-authoring/draft.json --port 2722
```

Task Studio writes drafts only after **Save draft revision** is selected and runs Harbor only
after **Run Harbor validation** is selected. **Export Harbor task** refuses to overwrite an
existing task directory.

## CLI workflow

```bash
uv run harbor-marimo verifier examples/science-task-authoring/draft.json
uv run harbor-marimo export-task examples/science-task-authoring/draft.json \
  --output outputs/harbor-tasks/bayesian-posterior-convergence
uv run harbor-marimo validate-task \
  outputs/harbor-tasks/bayesian-posterior-convergence --env docker
```

`validate-task` prints commands by default. Use `--run` to execute them. For a configured
CoreWeave environment, select it in Task Studio or use `--env cwsandbox`; sandbox creation,
credentials, task execution, and result collection remain downstream Harbor responsibilities.

## Outputs and boundaries

- The exported directory follows Harbor's task layout and contains `task.toml`,
  `instruction.md`, `environment/`, `solution/`, and `tests/`.
- The generated verifier is isolated in Harbor's verifier environment and consumes task
  artifacts as untrusted data.
- A sibling `*.review-profile.json` carries the same acceptance criteria into the existing
  scientific result-review app.
- Draft history and later expert reviews are sidecars; neither mutates an original Harbor job.
- An independent scientist should review the task before it becomes a benchmark item. Task
  authors may test their own oracle, but author validation is not independent approval.

Continue with the [independent task-review workflow](task-review.md) and review the
[security and collaboration boundaries](task-security.md) before benchmark publication.
