"""Plain-language terms used in scientific expert review."""

from __future__ import annotations

from acto.profiles import ReviewProfile


DEFAULT_SCIENCE_GLOSSARY = {
    "Harbor reward": (
        "An automated task signal. It is evidence, not a substitute for scientific judgment."
    ),
    "Verifier": "Automated checks applied to the agent result after execution.",
    "Artifact": "A file collected from the agent workspace with Harbor provenance.",
    "R-hat": (
        "A convergence diagnostic; values close to 1.0 generally indicate better "
        "agreement between sampling chains."
    ),
    "Effective sample size": (
        "An estimate of the independent information represented by correlated samples."
    ),
    "Confidence": (
        "The reviewer's confidence in the recorded expert verdict, not model confidence."
    ),
}


def science_glossary(profile: ReviewProfile | None = None) -> dict[str, str]:
    """Return defaults overlaid with domain-authored definitions."""

    values = dict(DEFAULT_SCIENCE_GLOSSARY)
    if profile:
        values.update(profile.glossary)
    return values
