# Scientific review example

This synthetic Harbor job demonstrates the provider-neutral science review workflow. It
contains a converged and a non-converged model-fitting trial with collected summaries and
verifier diagnostics. It is an interface fixture, not a Terminal-Bench Science task.

```bash
uv run harbor-marimo review examples/science-review/demo_data/harbor_job \
  --domain science \
  --review-dir outputs/science-reviews
```
