# Assess Bayesian posterior convergence

## Scientific context

Reliable convergence assessment is necessary before posterior estimates can support a scientific conclusion. This task tests whether an agent can produce both a result and the diagnostic evidence needed to trust it.

## Task

Fit the supplied Bayesian model and report posterior estimates. Create results/posterior_summary.csv with parameter, mean, r_hat, and ess columns, and results/convergence.json with an overall status. Report converged only when every R-hat is at most 1.01 and every effective sample size is at least 400.

## Required deliverables

- `results/posterior_summary.csv` (csv, required) — Posterior estimates and sampling diagnostics for every model parameter.
- `results/convergence.json` (json, required) — Machine-readable convergence conclusion.

## Completion

Place the requested outputs at the paths above. Evaluation checks the final scientific outputs, not the particular method used to produce them.
