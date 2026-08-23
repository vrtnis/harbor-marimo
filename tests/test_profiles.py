import json
from pathlib import Path
import tempfile
import unittest

from harbor_marimo.profiles import ReviewProfile, load_review_profile


class ReviewProfileTests(unittest.TestCase):
    def test_example_science_profile_is_valid(self) -> None:
        root = Path(__file__).resolve().parents[1]
        profile = load_review_profile(
            root / "examples" / "science-review" / "review_profile.json"
        )

        self.assertEqual(profile.title, "Bayesian Model Validation")
        self.assertEqual(len(profile.acceptance_criteria), 4)
        self.assertIn("R-hat", profile.glossary)

    def test_loads_typed_profile_and_matches_artifact_suffix(self) -> None:
        payload = {
            "title": "Bayesian validation",
            "question": "Did the sampler converge?",
            "acceptance_criteria": [
                {"id": "convergence", "label": "Chains converged"}
            ],
            "artifact_labels": {
                "posterior.csv": {
                    "label": "Posterior summary",
                    "guidance": "Check R-hat.",
                }
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            profile = load_review_profile(path)

        self.assertEqual(profile.title, "Bayesian validation")
        self.assertEqual(profile.acceptance_criteria[0].id, "convergence")
        presentation = profile.artifact_presentation("artifacts/workspace/posterior.csv")
        self.assertIsNotNone(presentation)
        self.assertEqual(presentation.label, "Posterior summary")

    def test_rejects_duplicate_criterion_ids(self) -> None:
        with self.assertRaisesRegex(ValueError, "unique"):
            ReviewProfile.from_dict(
                {
                    "title": "Review",
                    "acceptance_criteria": [
                        {"id": "same", "label": "First"},
                        {"id": "same", "label": "Second"},
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
