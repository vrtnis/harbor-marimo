# Architecture

`harbor-marimo` is the read-only analysis integration over Harbor output. The `acto`
package adds task authoring and expert review applications to that generic evidence layer.

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

## Package responsibilities

- `loader.py`, `models.py`, and `normalize.py` understand Harbor and ATIF evidence, not
  finance or science semantics.
- `acto/domains/` interprets artifacts and checks for a particular expert audience. Domain
  checks do not replace Harbor verifier rewards.
- `acto/reviews/` owns versioned judgments and evidence references. Its JSON store writes
  outside the Harbor job directory.
- `acto/apps/` contains the Task Studio, Task Review, and result-review Marimo applications.
- `harbor_marimo/apps/analysis.py` remains the generic evidence-analysis application.
- `plugin.py` is an optional, non-fatal handoff from Harbor. It never starts a long-lived
  Marimo server inside a worker process.

## Compatibility contract

The strongest contract is the saved Harbor job format: job and trial results, ATIF
trajectories, verifier output, and collected artifacts. The optional Harbor plugin is a
thin version-sensitive adapter; provider-specific sandbox SDKs remain Harbor's concern.

The loader tolerates incomplete jobs and records missing or unsafe evidence as
diagnostics. It does not execute collected artifacts. Domain previews are bounded and
specialized binary formats require explicit renderers.
