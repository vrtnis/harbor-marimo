"""Expert-oriented trial labels and comparison rows."""

from __future__ import annotations

from typing import Any, Iterable, Mapping


def trial_options(trials: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    return {
        f"Attempt {index} · {_outcome_label(trial.get('primary_reward'))}": str(
            trial["trial_id"]
        )
        for index, trial in enumerate(trials, start=1)
    }


def expert_comparison_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "attempt": f"Attempt {index}",
            "automated outcome": _outcome_label(row.get("reward")),
            "reward": row.get("reward"),
            "collected evidence": row.get("artifacts", 0),
            "verifier outputs": row.get("verifier_files", 0),
        }
        for index, row in enumerate(rows, start=1)
    ]


def _outcome_label(reward: Any) -> str:
    if reward == 1 or reward == 1.0:
        return "Verifier passed"
    if reward == 0 or reward == 0.0:
        return "Expert attention"
    return "Unscored"
