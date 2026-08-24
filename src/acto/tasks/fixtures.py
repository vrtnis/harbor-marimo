"""Exercise authored valid and invalid examples against task contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .artifacts import ArtifactIssue, inspect_artifact_contract
from .models import TaskDraft, VerifierFixture
from .verifier import CheckResult, evaluate_checks


@dataclass(frozen=True)
class FixtureResult:
    name: str
    expected_pass: bool
    actual_pass: bool
    matched: bool
    source: str
    explanation: str
    contract_issues: tuple[ArtifactIssue, ...] = ()
    checks: tuple[CheckResult, ...] = ()


def evaluate_fixture(
    draft: TaskDraft,
    draft_root: str | Path,
    fixture: VerifierFixture,
) -> FixtureResult:
    base = Path(draft_root).expanduser().resolve()
    source = (base / fixture.source).resolve()
    if not source.is_relative_to(base) or not source.is_dir():
        issues = (
            ArtifactIssue(fixture.source, "invalid_fixture", "Fixture directory is unavailable."),
        )
        return FixtureResult(
            fixture.name,
            fixture.expected_pass,
            False,
            fixture.expected_pass is False,
            fixture.source,
            fixture.explanation,
            contract_issues=issues,
        )
    contract_issues = tuple(
        issue
        for contract in draft.artifacts
        for issue in inspect_artifact_contract(source, contract)
    )
    checks = evaluate_checks(source, draft.checks)
    actual_pass = not contract_issues and bool(checks) and all(item.passed for item in checks)
    return FixtureResult(
        fixture.name,
        fixture.expected_pass,
        actual_pass,
        actual_pass == fixture.expected_pass,
        fixture.source,
        fixture.explanation,
        contract_issues=contract_issues,
        checks=checks,
    )


def evaluate_fixtures(
    draft: TaskDraft, draft_root: str | Path
) -> tuple[FixtureResult, ...]:
    return tuple(evaluate_fixture(draft, draft_root, fixture) for fixture in draft.fixtures)
