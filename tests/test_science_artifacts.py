from pathlib import Path
import unittest

from harbor_marimo import load
from harbor_marimo.domains.science import ScienceAdapter, classify_artifact


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "examples" / "financial-review" / "demo_data" / "harbor_job"


class ScienceArtifactTests(unittest.TestCase):
    def test_scientific_formats_are_classified_without_execution(self):
        cases = {
            "results.csv": ("table", True),
            "posterior.nc": ("array", False),
            "structure.pdb": ("molecule", True),
            "model.onnx": ("model", False),
        }
        for destination, expected in cases.items():
            with self.subTest(destination=destination):
                classification = classify_artifact(
                    {
                        "destination": destination,
                        "path": str(ROOT / destination),
                        "safe": True,
                        "exists": True,
                    }
                )
                self.assertEqual(
                    (classification.kind, classification.previewable), expected
                )

    def test_unsafe_artifacts_are_never_previewable(self):
        classification = classify_artifact(
            {
                "destination": "../../secret.csv",
                "path": None,
                "safe": False,
                "exists": False,
            }
        )

        self.assertFalse(classification.previewable)
        self.assertIsNone(classification.path)
        self.assertIn("trial boundary", classification.reason or "")

    def test_adapter_retains_harbor_provenance(self):
        bundle = load(JOB)

        view = ScienceAdapter().build_view(bundle)

        self.assertEqual(view.domain, "science")
        self.assertEqual(len(view.evidence), 3)
        self.assertTrue(all(item.job_id == bundle.jobs[0].id for item in view.evidence))


if __name__ == "__main__":
    unittest.main()
