"""Summaries for the local verifier fixture workbench."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .fixtures import FixtureResult, evaluate_fixtures
from .models import TaskDraft


@dataclass(frozen=True)
class FixtureSuiteReport:
    results: tuple[FixtureResult, ...]
    requirements: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.requirements

    @property
    def passed(self) -> bool:
        return self.complete and bool(self.results) and all(item.matched for item in self.results)

    def rows(self) -> list[dict[str, Any]]:
        return [
            {
                "fixture": item.name,
                "expected": "Pass" if item.expected_pass else "Fail",
                "actual": "Pass" if item.actual_pass else "Fail",
                "matched": item.matched,
                "contract issues": len(item.contract_issues),
                "failed checks": sum(not check.passed for check in item.checks),
                "explanation": item.explanation,
            }
            for item in self.results
        ]


def run_fixture_workbench(
    draft: TaskDraft, draft_root: str | Path
) -> FixtureSuiteReport:
    requirements: list[str] = []
    if not any(item.expected_pass for item in draft.fixtures):
        requirements.append("Add at least one known-valid fixture.")
    if not any(not item.expected_pass for item in draft.fixtures):
        requirements.append("Add at least one known-invalid or no-op fixture.")
    if not draft.checks:
        requirements.append("Add at least one machine-verifiable check.")
    return FixtureSuiteReport(evaluate_fixtures(draft, draft_root), tuple(requirements))
