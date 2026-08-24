"""Packaged Terminal-Bench Science task template discovery."""

from __future__ import annotations

from pathlib import Path


REQUIRED_TASK_FILES = (
    "task.toml",
    "instruction.md",
    "environment/Dockerfile",
    "solution/solve.sh",
    "tests/Dockerfile",
    "tests/test.sh",
)


def task_template_root(name: str = "terminal-bench-science") -> Path:
    root = Path(__file__).with_name("templates") / name
    missing = [relative for relative in REQUIRED_TASK_FILES if not (root / relative).is_file()]
    if missing:
        raise FileNotFoundError(f"Task template {name!r} is incomplete: {', '.join(missing)}")
    return root
