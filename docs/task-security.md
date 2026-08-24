# Task-authoring security and collaboration responsibilities

## Trust model

Task instructions, artifacts, oracle scripts, verifier code, and Dockerfiles are untrusted
benchmark inputs. The Marimo authoring and task-review apps display or structurally inspect
them; they do not import or execute task code. File resolution is constrained to the selected
task directory, text previews are size-bounded, and every file receives a SHA-256 digest in
the review inventory.

Known-good and known-bad fixture testing evaluates only the supported declarative checks.
The generated verifier executes later in Harbor's separate verifier environment. Oracle,
nop, agent, container, and cloud-sandbox execution occurs only through Harbor and only after
the user explicitly selects **Run Harbor validation** or passes `validate-task --run`.

## Ownership responsibilities

- Task Studio owns versioned draft sidecars and deterministic bundle generation.
- Harbor owns task execution, sandbox selection, credentials, resource lifecycle, artifact
  collection, and automated rewards.
- CoreWeave is a Harbor environment choice (`cwsandbox`), not infrastructure configured by
  this repository.
- Task Review owns independent, evidence-linked judgments about benchmark-item quality.
- Science Review owns evidence-linked judgments about agent results after a Harbor run.

Neither review app mutates the canonical task or Harbor job. Publishing a task, merging it
into a benchmark dataset, granting reviewers access, and resolving organizational conflicts
remain benchmark-governance responsibilities outside this local repository.

## Collaboration responsibilities

Task authors may revise in response to review, but prior sidecars remain part of the audit
trail. Domain and technical review should be performed by people with appropriate expertise
who are independent of the task author. Final approval should confirm both review streams,
licensing/provenance, and representative Harbor calibration runs before public release.
