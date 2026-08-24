# Scientific review example

This synthetic Harbor job demonstrates the provider-neutral science review workflow. It
contains a converged and a non-converged model-fitting trial with collected summaries and
verifier diagnostics. It is an interface fixture, not a Terminal-Bench Science task.

```bash
uv run acto review-results examples/science-review/demo_data/harbor_job \
  --domain science \
  --profile examples/science-review/review_profile.json \
  --guided \
  --review-dir outputs/science-reviews
```

The profile is separate from the synthetic Harbor job. It supplies expert-facing copy and
criteria while the loader continues to consume standard Harbor output. Remove `--guided`
for the normal review experience, or add `--developer` to expose local source and sidecar
paths while debugging.
