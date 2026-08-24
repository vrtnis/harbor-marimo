"""Declarative scientific verifier checks used by fixtures and generated tests."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Callable

from .models import VerifierCheck


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    passed: bool
    message: str
    actual: Any = None


def evaluate_check(root: str | Path, check: VerifierCheck) -> CheckResult:
    base = Path(root).expanduser().resolve()
    artifact = (base / check.artifact).resolve()
    if not artifact.is_relative_to(base):
        return CheckResult(check.id, False, "Artifact path escapes the verifier root.")
    if check.type == "file_exists":
        return CheckResult(check.id, artifact.is_file(), "Required artifact file exists." if artifact.is_file() else "Required artifact file is missing.")
    if not artifact.is_file():
        return CheckResult(check.id, False, f"Artifact {check.artifact!r} is missing.")
    try:
        handler = _HANDLERS[check.type]
    except KeyError:
        return CheckResult(check.id, False, f"Unsupported verifier check type: {check.type}")
    try:
        return handler(artifact, check)
    except (OSError, UnicodeError, ValueError, TypeError, csv.Error, json.JSONDecodeError) as exc:
        return CheckResult(check.id, False, f"Verifier check could not read its artifact: {exc}")


def evaluate_checks(
    root: str | Path, checks: tuple[VerifierCheck, ...]
) -> tuple[CheckResult, ...]:
    return tuple(evaluate_check(root, check) for check in checks if not check.expert_only)


def _csv_columns(path: Path, check: VerifierCheck) -> CheckResult:
    required = {str(item) for item in check.parameters.get("columns") or ()}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        header = set(next(csv.reader(handle), []))
    missing = sorted(required - header)
    return CheckResult(
        check.id,
        not missing,
        "Required CSV columns are present." if not missing else f"Missing CSV columns: {', '.join(missing)}",
        sorted(header),
    )


def _column_bound(path: Path, check: VerifierCheck, *, minimum: bool) -> CheckResult:
    column = str(check.parameters["column"])
    threshold = float(check.parameters["value"])
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    values = [float(row[column]) for row in rows]
    if not values or not all(math.isfinite(value) for value in values):
        return CheckResult(check.id, False, f"Column {column!r} has no finite values.", values)
    actual = min(values) if minimum else max(values)
    passed = actual >= threshold if minimum else actual <= threshold
    operator = ">=" if minimum else "<="
    return CheckResult(
        check.id,
        passed,
        f"Observed {column}={actual:g}; required {operator} {threshold:g}.",
        actual,
    )


def _column_min(path: Path, check: VerifierCheck) -> CheckResult:
    return _column_bound(path, check, minimum=True)


def _column_max(path: Path, check: VerifierCheck) -> CheckResult:
    return _column_bound(path, check, minimum=False)


def _json_equals(path: Path, check: VerifierCheck) -> CheckResult:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        return CheckResult(check.id, False, "Expected a JSON object.")
    field = str(check.parameters["field"])
    expected = check.parameters.get("value")
    actual = value.get(field)
    return CheckResult(
        check.id,
        actual == expected,
        f"JSON field {field!r} {'matches' if actual == expected else 'does not match'} the expected value.",
        actual,
    )


_HANDLERS: dict[str, Callable[[Path, VerifierCheck], CheckResult]] = {
    "csv_columns": _csv_columns,
    "column_min": _column_min,
    "column_max": _column_max,
    "json_equals": _json_equals,
}
