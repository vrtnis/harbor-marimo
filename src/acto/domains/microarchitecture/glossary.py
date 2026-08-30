"""Plain-language terms for CPU design-space-exploration review."""

from __future__ import annotations

from acto.profiles import ReviewProfile
from ..science import science_glossary


MICROARCHITECTURE_GLOSSARY = {
    "IPC": "Instructions per cycle, a measure of processor throughput.",
    "IPC MAPE": (
        "Mean absolute percentage error between predicted and measured IPC; lower is better."
    ),
    "Kendall tau-b": (
        "Agreement between predicted and measured design rankings; higher is better."
    ),
    "Top-1 normalized simple regret": (
        "Performance lost by selecting the predicted-best design instead of the actual best; "
        "lower is better."
    ),
    "ONNX": "A portable model format used here for the submitted IPC surrogate.",
    "Design-space exploration": (
        "Comparing candidate processor designs before more expensive simulation or evaluation."
    ),
}


def microarchitecture_glossary(profile: ReviewProfile | None = None) -> dict[str, str]:
    values = science_glossary(profile)
    values.pop("R-hat", None)
    values.pop("Effective sample size", None)
    values.update(MICROARCHITECTURE_GLOSSARY)
    if profile:
        values.update(profile.glossary)
    return values
