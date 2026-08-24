# Architecture

`harbor-marimo` is a read-only analysis and expert-review layer over Harbor output.

The domain-expert applications are organized as the separate `acto` package inside this
repository. See [Acto package structure](acto-package.md) for the package responsibilities
and compatibility policy.

```text
Harbor execution (Docker or cloud sandbox)
                |
                v
       canonical local job directory
                |
                v
     loader -> models -> normalized tables
                |
       +--------+---------+
       |                  |
 generic analysis     domain adapters
                          |
                 +--------+--------+
                 |                 |
          financial review   science review
                 |                 |
                 +--------+--------+
                          |
                 external review sidecars
```

## Package boundaries

- `loader.py`, `models.py`, and `normalize.py` understand Harbor and ATIF evidence, not
  finance or science semantics.
- `domains/` interprets artifacts and checks for a particular expert audience. Domain
  checks do not replace Harbor verifier rewards.
- `reviews/` owns versioned judgments and evidence references. Its JSON store writes
  outside the Harbor job directory.
- `apps/` contains installable Marimo notebooks. The CLI selects an app without changing
  the underlying job.
- `plugin.py` is an optional, non-fatal handoff from Harbor. It never starts a long-lived
  Marimo server inside a worker process.

## Compatibility contract

The strongest contract is the saved Harbor job format: job and trial results, ATIF
trajectories, verifier output, and collected artifacts. The optional Harbor plugin is a
thin version-sensitive adapter; provider-specific sandbox SDKs remain Harbor's concern.

The loader tolerates incomplete jobs and records missing or unsafe evidence as
diagnostics. It does not execute collected artifacts. Domain previews are bounded and
specialized binary formats require explicit renderers.
