# Expert review records

Expert reviews are independent judgments linked to Harbor evidence. They are not verifier
rewards and do not rewrite `result.json`, `trajectory.json`, manifests, or artifacts.

```bash
harbor-marimo review <job> --domain financial --review-dir outputs/reviews
harbor-marimo review <job> --domain science --review-dir outputs/reviews
```

The JSON sidecar layout is:

```text
<review-dir>/
  <job-id>/
    <trial-id>/
      <review-id>.json
```

A record contains:

- a versioned schema and stable review identifier;
- job, trial, and domain provenance;
- approve, reject, or needs-follow-up verdict;
- reviewer, rationale, confidence, and timestamps;
- evidence references to artifacts, verifier output, trajectory steps, or domain
  locations such as a workbook cell.

Saving another decision for the same job, trial, and domain updates the current record
atomically while retaining its creation identity. Review directories may contain names,
notes, and absolute artifact paths; treat them as potentially sensitive and sanitize them
before publication.
