import tempfile
from pathlib import Path
import unittest

from harbor_marimo import load
from harbor_marimo.domains.science import (
    ScienceAdapter,
    compare_trials,
    diagnostic_findings,
    preview_artifact,
)
from harbor_marimo.profiles import load_review_profile


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "examples" / "financial-review" / "demo_data" / "harbor_job"
SCIENCE_JOB = ROOT / "examples" / "science-review" / "demo_data" / "harbor_job"


class ScienceDomainTests(unittest.TestCase):
    def test_table_preview_is_bounded(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "posterior.csv"
            path.write_text("parameter,mean\na,1\nb,2\nc,3\n", encoding="utf-8")

            preview = preview_artifact(
                {
                    "destination": path.name,
                    "path": str(path),
                    "safe": True,
                    "exists": True,
                },
                max_rows=2,
            )

            self.assertEqual(preview.kind, "table")
            self.assertEqual(len(preview.rows), 2)
            self.assertTrue(preview.truncated)

    def test_python_artifacts_are_read_as_text_not_executed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "analysis.py"
            path.write_text("raise RuntimeError('must not execute')", encoding="utf-8")

            preview = preview_artifact(
                {
                    "destination": path.name,
                    "path": str(path),
                    "safe": True,
                    "exists": True,
                }
            )

            self.assertIn("must not execute", preview.text or "")

    def test_trial_comparison_keeps_reward_and_behavior_separate(self):
        rows = compare_trials(load(JOB))

        self.assertEqual(len(rows), 3)
        self.assertEqual([row["reward"] for row in rows], [1.0, 1.0, 0.0])
        self.assertTrue(all(row["tool_calls"] == 3 for row in rows))

    def test_science_fixture_exposes_convergence_evidence(self):
        bundle = load(SCIENCE_JOB)

        findings = diagnostic_findings(bundle, trial_id="science-bad")

        self.assertEqual(len(compare_trials(bundle)), 2)
        self.assertIn("Reported convergence failure", {item.label for item in findings})

    def test_science_adapter_applies_optional_review_profile(self):
        profile = load_review_profile(
            ROOT / "examples" / "science-review" / "review_profile.json"
        )

        view = ScienceAdapter(profile).build_view(load(SCIENCE_JOB), trial_id="science-good")

        self.assertEqual(view.title, "Bayesian Model Validation")
        self.assertIn("posterior estimates", view.question)
        self.assertEqual(len(view.criteria), 4)
        posterior = next(item for item in view.evidence if "posterior_summary" in (item.technical_label or ""))
        self.assertEqual(posterior.label, "Posterior summary")
        self.assertIn("R-hat", posterior.review_guidance or "")
        self.assertTrue((posterior.technical_label or "").endswith("posterior_summary.csv"))


if __name__ == "__main__":
    unittest.main()
