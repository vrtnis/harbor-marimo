# Cloud sandbox compatibility

`harbor-marimo` consumes canonical Harbor job output and does not communicate with a
cloud sandbox provider. Harbor owns sandbox credentials, lifecycle, networking, remote
execution, artifact download, and verifier execution.

## CoreWeave Sandboxes

Install the opt-in provider dependency in the same environment as Harbor and the plugin:

```bash
uv sync --extra plugin --extra domain --extra coreweave
```

Configure CoreWeave for the Harbor process and run the job:

```powershell
$env:CWSANDBOX_API_KEY = "..."
uv run harbor run `
  -d "<dataset>" `
  -a "<agent>" `
  -m "<model>" `
  -e cwsandbox `
  -n 32 `
  --plugin marimo
```

The plugin runs in the local Harbor orchestrator. It does not run Marimo inside the
remote sandbox and does not keep a web server alive in the Harbor worker. When Harbor
finishes downloading the trial output, the plugin prints the local analysis handoff.

```bash
uv run acto review-results <local-job-directory> \
  --domain science \
  --review-dir outputs/reviews
```

The review process does not require `CWSANDBOX_API_KEY`.

## Artifact contract

For remote environments, write important outputs to `/logs/artifacts/` or configure
Harbor artifact collection. Harbor downloads those files into each local trial directory;
`harbor-marimo` only previews safe, locally collected paths.

CoreWeave currently supports single-container Harbor tasks. Docker Compose tasks must use
a provider that supports multi-container environments. CoreWeave tasks also need a
compatible prebuilt/default image with `/bin/bash`; Dockerfile-only tasks without a
prebuilt image are rejected by Harbor's provider adapter.

See Harbor's current [cloud sandbox](https://www.harborframework.com/docs/run-jobs/cloud-sandboxes)
and [artifact collection](https://www.harborframework.com/docs/run-jobs/results-and-artifacts)
documentation for provider capabilities and task configuration.
