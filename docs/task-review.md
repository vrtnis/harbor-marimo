# Scientific benchmark task review

Task review and agent-result review answer different questions:

| Stage | Question | Responsible role | Record |
| --- | --- | --- | --- |
| Author validation | Does the draft, oracle, fixture set, and verifier behave as intended? | Task author | Task-review sidecar marked `author_validation` |
| Domain review | Is the task scientifically meaningful and correct? | Unconflicted domain expert | Evidence-linked task-review sidecar |
| Technical review | Is the task reproducible, isolated, safe, and correctly verified? | Unconflicted technical reviewer | Evidence-linked task-review sidecar |
| Final approval | Are independent findings resolved and is release provenance complete? | Unconflicted benchmark approver | Final task-review sidecar |
| Result review | Is an agent's submitted result scientifically acceptable for this task? | Domain expert who did not produce that result | Harbor job review sidecar |

An author can create the task, write the oracle, define fixtures, run verifier tests, and
record an author-validation review. The application deliberately refuses to treat that
record as independent approval. Independent and final roles also cannot be assigned to a
reviewer whose normalized name is the task author's name, and an approving reviewer cannot
have a declared conflict.

Open the included task:

```bash
uv run acto review-task \
  examples/science-task-review/bayesian-posterior-convergence \
  --review-dir outputs/task-reviews \
  --port 2722
```

The reviewer reads the instruction, task configuration, verifier, oracle, and environment
as inert text; completes the role-specific Terminal-Bench Science rubric; links findings to
specific evidence keys; declares conflicts; and records a decision. Reviews are atomic JSON
sidecars outside the Harbor task.

After Harbor runs agents against an approved task, reuse its exported criteria in result
review:

```bash
uv run acto review-results outputs/jobs/example-job \
  --domain science \
  --task outputs/harbor-tasks/bayesian-posterior-convergence \
  --review-dir outputs/result-reviews
```

The `--task` option resolves the adjacent review profile produced during export. This keeps
the task's acceptance criteria, artifact labels, and expert guidance consistent between
benchmark design and grading without making automated reward equivalent to scientific truth.
