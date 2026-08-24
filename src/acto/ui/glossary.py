"""Accessible glossary presentation."""

from __future__ import annotations

from collections.abc import Mapping


def glossary_markdown(values: Mapping[str, str]) -> str:
    return "\n\n".join(f"**{term}**  \n{definition}" for term, definition in values.items())
