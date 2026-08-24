"""Harbor-compatible scientific benchmark task authoring."""

from .artifacts import ArtifactIssue, inspect_artifact_contract
from .generator import generate_verifier_script
from .fixtures import FixtureResult, evaluate_fixture, evaluate_fixtures
from .models import (
    ArtifactContract,
    ArtifactField,
    ScientificBrief,
    TaskDraft,
    TaskMetadata,
    VerifierCheck,
    VerifierFixture,
)
from .render import render_instruction, render_task_toml
from .store import TaskDraftStore
from .templates import REQUIRED_TASK_FILES, task_template_root
from .validation import (
    HarborValidationCommand,
    HarborValidationRun,
    harbor_validation_plan,
    run_harbor_validation,
)
from .verifier import CheckResult, evaluate_check, evaluate_checks
from .workbench import FixtureSuiteReport, run_fixture_workbench

__all__ = [
    "ArtifactContract",
    "ArtifactField",
    "ArtifactIssue",
    "CheckResult",
    "FixtureResult",
    "FixtureSuiteReport",
    "HarborValidationCommand",
    "HarborValidationRun",
    "REQUIRED_TASK_FILES",
    "render_instruction",
    "render_task_toml",
    "run_fixture_workbench",
    "ScientificBrief",
    "TaskDraft",
    "TaskDraftStore",
    "task_template_root",
    "inspect_artifact_contract",
    "TaskMetadata",
    "VerifierCheck",
    "VerifierFixture",
    "evaluate_check",
    "evaluate_checks",
    "evaluate_fixture",
    "evaluate_fixtures",
    "generate_verifier_script",
    "harbor_validation_plan",
    "run_harbor_validation",
]
