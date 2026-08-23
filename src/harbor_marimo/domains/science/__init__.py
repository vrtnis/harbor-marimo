"""Scientific artifact interpretation for Terminal-Bench-style workflows."""

from .artifacts import ArtifactClassification, classify_artifact
from .adapter import ScienceAdapter
from .comparison import DiagnosticFinding, compare_trials, diagnostic_findings
from .previews import ArtifactPreview, preview_artifact

__all__ = [
    "ArtifactClassification",
    "ArtifactPreview",
    "DiagnosticFinding",
    "ScienceAdapter",
    "classify_artifact",
    "compare_trials",
    "diagnostic_findings",
    "preview_artifact",
]
