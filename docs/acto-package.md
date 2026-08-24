# Acto package structure

This repository contains two cooperating Python packages:

- `harbor_marimo` reads and normalizes Harbor jobs, exports generic evidence tables,
  provides the generic analysis application, and registers the optional Harbor plugin.
- `acto` provides the domain-expert applications and methods built on that evidence:
  task authoring, verifier fixtures, independent task review, result review, and
  financial and scientific interpretation.

Marimo remains the application runtime. Harbor remains the external task runner and
canonical job format. The Acto package imports the generic Harbor-Marimo integration;
the loader, normalized models, export API, and Harbor plugin do not require Acto.

```text
Harbor jobs and task bundles
            |
            v
     harbor_marimo
   loader and evidence API
            |
            v
          acto
 task studio and reviews
            |
            v
    Marimo applications
```

## Compatibility

The reorganization does not change Harbor task bundles, saved job formats, review JSON
schemas, or review-directory conventions. Existing `harbor-marimo` commands and Python
imports remain available as compatibility aliases while the equivalent `acto` commands
and modules become the preferred expert-workflow interface.

The intended command ownership is:

| Command | Responsibility |
| --- | --- |
| `harbor-marimo view` | Generic Harbor evidence analysis |
| `harbor-marimo export` | Generic normalized evidence export |
| `acto studio` | Domain-expert task and verifier authoring |
| `acto review-task` | Independent benchmark task review |
| `acto review-results` | Domain-expert grading of agent results |

Provider-specific cloud execution, including CoreWeave sandbox creation and credentials,
continues to be handled by Harbor after Acto exports a standard task bundle.
